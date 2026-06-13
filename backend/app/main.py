import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import init_db, SessionLocal, set_current_org, set_default_org
from app.routers import deals, documents, issues, analysis, qa, reports, users, clients, activity
from app.web.routes import router as web_router
from app.middleware.auth import APIKeyMiddleware
from app.middleware.audit import AuditMiddleware
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.seed import get_or_create_default_org

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("ma_dd")

app = FastAPI(title=settings.brand_name, version="0.3.0", docs_url="/api/docs", redoc_url="/api/redoc")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    max_requests=settings.rate_limit_max,
    window_seconds=settings.rate_limit_window,
)
app.add_middleware(APIKeyMiddleware)
app.add_middleware(AuditMiddleware)

app.include_router(deals.router)
app.include_router(documents.router)
app.include_router(issues.router)
app.include_router(analysis.router)
app.include_router(qa.router)
app.include_router(reports.router)
app.include_router(users.router)
app.include_router(clients.router)
app.include_router(activity.router)
app.include_router(web_router)

static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

storage = Path(settings.storage_dir)
storage.mkdir(parents=True, exist_ok=True)
(Path(__file__).parent.parent / "data").mkdir(exist_ok=True)


@app.on_event("startup")
def on_startup():
    try:
        settings.validate()
    except ValueError as e:
        logger.critical("Configuration validation failed: %s", e)
        raise

    init_db()
    db = SessionLocal()
    try:
        org = get_or_create_default_org(db)
        set_current_org(org.id)
        set_default_org(org.id)
        logger.info("Default organization ready: %s (%s)", org.name, org.id)
    except Exception:
        logger.exception("Failed to initialize organization")
        raise
    finally:
        db.close()

    if settings.encrypt_documents and not settings.encryption_key:
        logger.warning("ENCRYPT_DOCUMENTS=true but ENCRYPTION_KEY is not set")

    logger.info(
        "%s started — auth=%s encryption=%s dpdp=%s model=%s",
        settings.brand_name,
        settings.auth_enabled,
        settings.encrypt_documents,
        settings.dpdp_compliance,
        settings.openai_model,
    )


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "0.3.0", "brand": settings.brand_name}
