import json
from typing import Optional
from openai import OpenAI

from app.config import settings
from app.services.chunking import chunk_text

ANALYSIS_PROMPT = """You are an M&A due diligence analyst specializing in INDIAN M&A transactions. Analyze the document using Indian legal and regulatory frameworks.

Document filename: {filename}
Workstream: {workstream}

CONSIDER THESE INDIAN FRAMEWORKS:

### Corporate (Companies Act 2013)
- Check compliance with Sections 185 (loans to directors), 186 (investments), 188 (RPTs), 134 (board report)
- Verify board resolutions are valid per Section 179-180
- Check CSR compliance (Section 135) if applicable
- Verify independent director requirements (Schedule IV, Section 149)
- Check related party transaction thresholds and approval requirements
- Verify statutory filings (MGT-14, AOC-4, MGT-7) are up to date

### Tax (Income Tax Act 1961 + CGST Act 2017)
- Verify TDS compliance (Sections 194C, 194J, 195) — non-compliance = 30% disallowance u/s 40(a)(ia)
- Check transfer pricing documentation (Section 92-94F) for international transactions
- Assess MAT exposure (Section 115JB)
- Verify GST registration and return filing (GSTR-3B, GSTR-9)
- Check GST input tax credit eligibility (Section 16, CGST Act)
- Assess potential reassessment risk under Sections 147-148 (6-year window)
- Verify withholding tax certificates for cross-border payments

### Regulatory (SEBI, RBI, FEMA, CCI)
- SEBI SAST (Takeover Code) implications at 25%+ acquisition
- SEBI LODR compliance if target is listed
- RBI/FEMA compliances for foreign investment/divestment
- CCI merger control if assets/turnover thresholds met
- FDI sectoral caps and conditionalities under Consolidated FDI Policy
- Pricing guidelines for shares issued to foreign residents

### Employment & Labour (Indian Labour Laws)
- Verify PF registration and contribution compliance (EPF Act 1952)
- Check ESI registration (ESI Act 1948)
- Verify gratuity compliance (Payment of Gratuity Act 1972)
- Check bonus compliance (Payment of Bonus Act 1965)
- Verify POSH Act 2013 compliance (ICC formation, annual report)
- Check contract labour registrations (CLRA Act 1970)
- Assess exposure from historical labour law violations

### Data & IT (DPDP Act 2023, IT Act 2000)
- DPDP Act 2023 compliance: consent, notice, data processing obligations
- Data localization requirements for sensitive data
- CERT-In incident reporting compliance
- IT Act 2000 Section 43A: compensation for data breach

### Intellectual Property (Indian IP Laws)
- Patent registrations (Patents Act 1970)
- Trademark registrations (Trade Marks Act 1999)
- Copyright registrations (Copyright Act 1957)
- IP assignment deeds and licensing agreements
- Check for pending IP litigation/oppositions

### Dispute Resolution (Arbitration Act 1996, CPC)
- Check pending litigation in Indian courts/NCLT/DRAT
- Verify arbitration clause validity (Arbitration and Conciliation Act 1996)
- Check limitation periods (Limitation Act 1963 — 3 years for contracts)
- Assess exposure from statutory notices/demands

Return a JSON object:
{{
  "summary": "2-3 sentence summary under INDIAN legal framework context",
  "key_terms": ["important terms, amounts, parties, Indian statutory references"],
  "red_flags": [
    {{
      "title": "title referencing the Indian law/regulation involved",
      "description": "detailed description with Indian legal context",
      "severity": "high|medium|low|info",
      "category": "compliance|financial|legal|operational|regulatory|other",
      "reference_text": "exact text that triggered this flag",
      "recommendation": "actionable recommendation under Indian law"
    }}
  ],
  "risks": "overall risk assessment under Indian regulatory framework"
}}

Only return valid JSON. No markdown fences. Assess risk based on INDIAN law, not common law standards.

Document text:
{text}"""


def analyze_document(
    filename: str,
    workstream: str,
    text: str,
    client=None,
) -> dict:
    if client is None:
        client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)

    if not text or len(text.strip()) < 50:
        return {
            "summary": "Document too short to analyze under Indian legal framework.",
            "key_terms": [],
            "red_flags": [],
            "risks": "Insufficient content for analysis.",
        }

    chunks = chunk_text(text)
    all_red_flags = []
    all_key_terms = set()
    summaries = []
    risks = []

    for chunk in chunks:
        try:
            resp = client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert M&A due diligence analyst specializing in Indian M&A, SEBI, RBI, Companies Act 2013, Income Tax Act 1961, DPDP Act 2023, and Indian labour laws. Always return valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": ANALYSIS_PROMPT.format(
                            filename=filename,
                            workstream=workstream,
                            text=chunk,
                        )
                    },
                ],
                temperature=0.2,
                max_tokens=4096,
            )
            content = resp.choices[0].message.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            result = json.loads(content)
            if result.get("summary"):
                summaries.append(result["summary"])
            if result.get("key_terms"):
                all_key_terms.update(k for k in result["key_terms"] if k)
            if result.get("red_flags"):
                flags_seen = {(f.get("title"), f.get("reference_text")) for f in all_red_flags}
                for rf in result["red_flags"]:
                    key = (rf.get("title"), rf.get("reference_text"))
                    if key not in flags_seen:
                        flags_seen.add(key)
                        all_red_flags.append(rf)
            if result.get("risks"):
                risks.append(result["risks"])
        except Exception:
            continue

    return {
        "summary": " ".join(summaries) if summaries else "Analysis completed.",
        "key_terms": list(all_key_terms),
        "red_flags": all_red_flags,
        "risks": " ".join(risks) if risks else "Risk assessment completed.",
    }
