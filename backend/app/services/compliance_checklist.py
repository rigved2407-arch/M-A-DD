INDIAN_COMPLIANCE_CHECKLIST = {
    "corporate": {
        "title": "Corporate Compliance (Companies Act 2013)",
        "items": [
            "Board meetings held at least 4 times a year (Section 173)",
            "Independent directors meet statutory requirements (Section 149)",
            "CSR committee constituted if applicable (Section 135)",
            "Related party transactions approved per Section 188",
            "Annual return (MGT-7) filed within 60 days of AGM",
            "Financial statements (AOC-4) filed within 30 days of AGM",
            "Board report includes Directors' Responsibility Statement",
            "Audit committee constituted (Section 177)",
            "Nomination and remuneration committee (Section 178)",
            "Loans to directors prohibited under Section 185",
            "Investments within limits of Section 186",
            "Deposits comply with Section 73-76",
        ],
    },
    "tax": {
        "title": "Tax Compliance (Income Tax Act 1961 + CGST 2017)",
        "items": [
            "Income tax returns filed for last 3 years",
            "TDS returns filed and TDS deposited on time (Section 194C/194J/195)",
            "TDS certificates issued to deductees",
            "Transfer pricing documentation maintained (Section 92E)",
            "MAT computation done (Section 115JB) if applicable",
            "GST returns (GSTR-3B, GSTR-9) filed on time",
            "GST input tax credit availed per Section 16",
            "E-invoicing compliance if turnover exceeds INR 5 Cr",
            "Tax audit completed (Section 44AB) if applicable",
            "Assessment orders reviewed and appeals filed if needed",
        ],
    },
    "regulatory": {
        "title": "Regulatory Compliance (SEBI, RBI, CCI)",
        "items": [
            "SEBI LODR compliance (if listed company)",
            "Shareholding pattern within prescribed limits",
            "Material events disclosed per Regulation 30",
            "FDI compliance if foreign investment exists",
            "FEMA reporting (FC-GPR, FC-TRS, annual returns)",
            "CCI combination filing if thresholds met",
            "Sector-specific regulatory approvals in place",
            "Environmental clearances (if applicable)",
        ],
    },
    "employment": {
        "title": "Employment & Labour Law Compliance",
        "items": [
            "PF registration and monthly contributions (EPF Act)",
            "ESI registration and contributions (ESI Act)",
            "Gratuity fund created (Payment of Gratuity Act)",
            "Bonus payments comply with Payment of Bonus Act",
            "POSH Act — ICC constituted, annual report filed",
            "Contract labour registrations (CLRA Act)",
            "Shop and establishment registration (state-specific)",
            "Factories Act compliance (if manufacturing)",
            "Standing orders certified (if 100+ workers)",
            "Minimum wages paid as per state schedule",
        ],
    },
    "data_protection": {
        "title": "Data Protection & IT (DPDP Act 2023)",
        "items": [
            "Privacy notice published as per Section 4",
            "Consent mechanism implemented (Section 6)",
            "Data retention policy defined (Section 9)",
            "Data principal rights mechanism in place",
            "Data Protection Officer appointed",
            "Data breach response plan documented",
            "CERT-In compliance for incident reporting",
            "Data localization for sensitive data",
            "Third-party data processor agreements in place",
        ],
    },
    "ip": {
        "title": "Intellectual Property",
        "items": [
            "Trademark registrations valid and renewed",
            "Patent registrations valid and maintained",
            "Copyright registrations in place",
            "IP licensing agreements documented",
            "No pending IP oppositions or litigation",
            "Domain names registered and renewed",
            "Trade secrets protected with NDAs",
        ],
    },
}


def get_compliance_checklist(deal_type: str = "M&A") -> dict:
    return INDIAN_COMPLIANCE_CHECKLIST


def get_compliance_summary(checked_items: dict[str, list[str]]) -> dict:
    total = 0
    checked = 0
    for category, items in checked_items.items():
        if category in INDIAN_COMPLIANCE_CHECKLIST:
            total += len(INDIAN_COMPLIANCE_CHECKLIST[category]["items"])
            checked += len(items)
    return {
        "total_items": total,
        "checked_items": checked,
        "completion_pct": round(checked / total * 100, 1) if total else 0,
    }
