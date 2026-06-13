# M&A Due Diligence AI

**AI-powered due diligence automation for Indian M&A transactions.** Built specifically for Indian law firms to streamline due diligence across all regulatory frameworks — Companies Act 2013, SEBI, RBI/FEMA, Income Tax Act, CGST, DPDP Act 2023, and more.

## Features

- **Deal Rooms** — Create and manage M&A transactions with client engagement tracking
- **Virtual Data Room** — Upload and organize documents by Indian M&A workstream
- **Auto-Classification** — AI categorizes documents into Legal, Financial, Commercial, Tax, HR, IT, Environmental, Insurance, Regulatory
- **AI Analysis** — Extract key terms, detect red flags, and auto-generate issues under Indian law
- **Indian Regulatory Coverage** — Companies Act 2013, SEBI SAST/LODR, FEMA, Income Tax Act, CGST, DPDP Act 2023, Labour Laws, CCI
- **Issue Tracker** — Log, categorize, and resolve due diligence issues
- **Q&A Assistant** — Ask questions about the deal, AI answers with document citations
- **DD Report** — Generate comprehensive due diligence reports (DOCX) with Indian deal considerations
- **DPDP Act 2023 Compliance** — Consent management, data subject requests, breach notifications
- **Multi-User** — Partner, Associate, Reviewer roles for law firm workflow
- **Client Management** — Track engagements per client
- **Audit Trail** — Full activity log per deal
- **White-Label** — Brandable for law firm resale

## Quick Start

```bash
# 1. Clone and configure
cp backend/.env.example backend/.env
# Edit backend/.env — set GROQ_API_KEY or OPENAI_API_KEY

# 2. Run with Docker
docker compose up --build

# 3. Open http://localhost:8000
```

## Manual Setup

```bash
# Python 3.12+
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
uvicorn app.main:app --reload --port 8000
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./data/ma_dd.db` |
| `GROQ_API_KEY` | Groq API key (free tier) | — |
| `OPENAI_API_KEY` | OpenAI API key | — |
| `ENCRYPTION_KEY` | AES-256 encryption key | — |
| `AUTH_ENABLED` | Enable API key auth | `false` |
| `DPDP_COMPLIANCE` | Enable DPDP Act features | `false` |
| `BRAND_NAME` | White-label app name | M&A Due Diligence AI |
| `FIRM_NAME` | Your law firm name | Your Law Firm |

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

## Deployment

```bash
# Production with Docker
docker compose up -d

# Run database migrations
docker compose exec app alembic upgrade head

# Or manually:
cd backend && alembic upgrade head
```

## Security

See [SECURITY.md](SECURITY.md) for production security setup including encryption, authentication, and data retention policies.

## License

Commercial license. For resale to Indian law firms. Contact the author for licensing terms.
