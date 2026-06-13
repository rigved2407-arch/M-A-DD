# Security Guide — M&A Due Diligence AI

## Overview

This tool handles **highly confidential M&A documents** (financials, IP, contracts, employee data). Security is critical — especially when deployed for Indian law firms handling sensitive client data.

## Production Security Checklist

```bash
# 1. Generate encryption key (for AES-256 at rest)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 2. Generate API key
python -c "import secrets; print(secrets.token_urlsafe(48))"

# 3. Generate admin password
python -c "import secrets; print(secrets.token_urlsafe(24))"

# 4. Set in .env
ENCRYPTION_KEY=<from step 1>
ENCRYPT_DOCUMENTS=true
AUTH_ENABLED=true
API_KEY=<from step 2>
AUDIT_ENABLED=true
DATA_RETENTION_DAYS=365
DPDP_COMPLIANCE=true
DATA_RESIDENCY=in
```

## Key Security Features

| Feature | Status | Configuration |
|---------|--------|---------------|
| AES-256 encryption at rest | Built-in | `ENCRYPT_DOCUMENTS=true` |
| API key authentication | Built-in | `AUTH_ENABLED=true` |
| Rate limiting | Built-in | `RATE_LIMIT_MAX=60` |
| File signature validation | Built-in | Automatic on upload |
| Audit logging | Built-in | `AUDIT_ENABLED=true` |
| Data retention | Built-in | `DATA_RETENTION_DAYS=365` |
| Azure OpenAI option | Built-in | For data residency requirements |
| DPDP/GDPR compliance | Built-in | `DPDP_COMPLIANCE=true` |
| Multi-tenant isolation | Built-in | Organization-based row-level filtering |
| HTTPS enforcement | Nginx | Deploy behind TLS termination |

## Deployment Security

1. **Always deploy behind HTTPS** — Use the provided nginx config with valid TLS certificates
2. **Use PostgreSQL in production** — SQLite is for local dev only
3. **Set strong passwords** — Generate all secrets using the commands above
4. **Enable encryption** — Set `ENCRYPT_DOCUMENTS=true` with a valid `ENCRYPTION_KEY`
5. **Enable auth** — Set `AUTH_ENABLED=true` with a strong `API_KEY`
6. **Configure CORS** — Restrict `CORS_ORIGINS` to your frontend domain
7. **Regular updates** — Keep dependencies updated with `pip-audit` or `safety`

## Data Residency (India)

For Indian law firm compliance:
- Set `DATA_RESIDENCY=in` for India-only data storage
- Set `DPDP_COMPLIANCE=true` to enable DPDP Act 2023 features
- Deploy on Indian cloud providers (AWS Mumbai, Azure Central India, GCP Mumbai)
- Use Azure OpenAI service for AI if data residency is a concern

## Incident Response

1. Audit logs capture all API activity — check `audit_logs` table
2. Breach notifications can be logged via the DPDP compliance module
3. Data retention auto-expiry prevents stale data accumulation
4. File uploads validate magic bytes to prevent type spoofing
