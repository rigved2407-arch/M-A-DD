from typing import Optional

from openai import OpenAI

from app.config import settings

WORKSTREAM_PROMPT = """Classify the following document into one of these M&A due diligence workstream categories.
Respond with ONLY a single word from this list: legal, financial, commercial, tax, hr, it, environmental, insurance, regulatory, other

RULES WITH INDIAN DOCUMENT TYPES:
- legal: Indian contracts (SHA, JVA, NDA, supply agreements), litigation documents (including Indian court/NCLT/DRAT filings), IP registrations (Indian Patents/Copyrights/Trademarks), board minutes (Companies Act 2013 compliant), legal opinions, due diligence reports
- financial: Indian financial statements (Schedule III format under Companies Act 2013), audit reports (CARO reports), revenue tax audit reports, cost audit reports, ICAI compliance certificates, standalone and consolidated financials
- commercial: Customer contracts, Indian distribution agreements, supply agreements, sales data, marketing materials, channel partner agreements, e-commerce marketplace agreements
- tax: Indian income tax returns (ITR), tax assessment orders (Section 143(3)), GST returns (GSTR-1/3B/9), TDS returns, transfer pricing documentation (Form 3CEB), advance pricing agreements, tax audit reports (Form 3CB/3CD), MAT computations, withholding tax certificates
- hr: Indian employment agreements (standing orders, state S&E Act compliance), ESOP schemes (Companies Act 2013 or SEBI norms), payroll data, PF/ESI/Gratuity/Bonus returns, POSH Act policy, labour law registrations (Factories Act, Contract Labour Act), shop and establishment registrations
- it: Software licenses, IT policies, Indian DPDP Act 2023 compliance documents, CERT-In compliance, cybersecurity policies, data localization evidence, source code escrow
- environmental: Indian environmental clearances (MoEF&CC), consent to operate (state PCB), environmental impact assessments, hazardous waste management (HW Rules 2016), water/air act compliance
- insurance: Indian insurance policies (IRDAI compliant), claims history, risk assessments, marine/ER/D&O/policyholder records
- regulatory: Indian regulatory filings (SEBI, RBI, CCI, IRDAI, TRAI, DoT), FEMA compliances, FDI approvals, CCI merger clearance, exchange control filings, licenses and permits, specific approvals under Indian regulations
- other: anything that doesn't fit above

Consider INDIAN statutory references when classifying. For example, a document discussing 'Form MGT-14' or 'Board Resolution under Section 188' is legal. A document with 'GSTR-3B' is tax.

Document filename: {filename}

First 3000 characters:
{text}"""

def classify_document(filename: str, text: str, client=None) -> str:
    if client is None:
        client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)
    try:
        resp = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are an M&A due diligence document classifier. Respond with ONLY one word."},
                {"role": "user", "content": WORKSTREAM_PROMPT.format(
                    filename=filename, text=text[:3000]
                )},
            ],
            temperature=0.1,
            max_tokens=10,
        )
        result = resp.choices[0].message.content.strip().lower()
        valid = ["legal", "financial", "commercial", "tax", "hr", "it",
                 "environmental", "insurance", "regulatory", "other"]
        return result if result in valid else "other"
    except Exception:
        return "other"

