import logging
from pathlib import Path
from pydantic_settings import BaseSettings

logger = logging.getLogger("ma_dd.config")


class Settings(BaseSettings):
    database_url: str = "sqlite:///./data/ma_dd.db"
    openai_api_key: str = ""
    openai_model: str = "llama-3.3-70b-versatile"
    openai_base_url: str = "https://api.groq.com/openai/v1"
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    storage_dir: str = "./data/storage"
    max_upload_size_mb: int = 100
    cors_origins: list[str] = ["http://localhost:3000"]
    encryption_key: str = ""
    encryption_salt: str = "ma-dd-ai-salt"
    encrypt_documents: bool = False
    auth_enabled: bool = False
    api_key: str = ""
    audit_enabled: bool = True
    data_retention_days: int = 365
    auto_delete_expired: bool = False
    llm_data_logging: bool = False
    llm_redact_pii: bool = False
    dpdp_compliance: bool = False
    data_residency: str = "local"
    rate_limit_max: int = 60
    rate_limit_window: int = 60
    log_level: str = "INFO"
    debug: bool = False

    brand_name: str = "M&A Due Diligence AI"
    brand_short: str = "MA-DD"
    firm_name: str = "Your Law Firm"
    firm_email: str = "contact@yourfirm.com"
    support_email: str = "support@yourfirm.com"

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""
    smtp_from: str = ""
    smtp_tls: bool = True
    notification_email: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def validate(self):
        errors = []
        if not self.database_url:
            errors.append("DATABASE_URL is required")
        if self.encrypt_documents and not self.encryption_key:
            errors.append("ENCRYPTION_KEY is required when ENCRYPT_DOCUMENTS=true")
        if not self.openai_api_key and not self.groq_api_key:
            errors.append("Either OPENAI_API_KEY or GROQ_API_KEY must be set")
        if self.rate_limit_max < 1:
            errors.append("RATE_LIMIT_MAX must be >= 1")
        if self.data_retention_days < 1:
            errors.append("DATA_RETENTION_DAYS must be >= 1")
        if self.dpdp_compliance and self.data_residency not in ("in", "local"):
            errors.append("DATA_RESIDENCY must be 'in' or 'local' for DPDP compliance")
        if errors:
            for e in errors:
                logger.error("Configuration error: %s", e)
            raise ValueError("Configuration validation failed:\n  - " + "\n  - ".join(errors))

    @property
    def llm_api_key(self) -> str:
        return self.groq_api_key or self.openai_api_key

    @property
    def llm_base_url(self) -> str:
        if self.groq_api_key:
            return "https://api.groq.com/openai/v1"
        return self.openai_base_url


settings = Settings()
