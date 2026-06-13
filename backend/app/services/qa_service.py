import json
from openai import OpenAI
from app.config import settings
from app.services.chunking import chunk_text

QA_PROMPT = """You are an M&A due diligence Q&A assistant specializing in Indian M&A transactions. You MUST answer based SOLELY on the provided document excerpts — do NOT use your training data.

CONSTRAINTS (strict — read carefully):
1. If the answer cannot be found in the excerpts below, say "I couldn't find information about this in the provided documents."
2. Every claim MUST be supported by a citation from the excerpts below.
3. If you cite a document, include the exact relevant excerpt and the filename.
4. Never make up legal citations or regulatory references — only use what's in the documents.

Indian M&A Context (use only for framing, NOT for generating facts not in the documents):
- Companies Act 2013, SEBI SAST/LODR, FEMA/RBI, Income Tax Act 1961, CGST 2017, DPDP Act 2023

Documents:
{documents}

Question: {question}

Return valid JSON only (no markdown):
{{
  "answer": "your detailed answer with citations inline",
  "citations": [
    {{"filename": "doc1.pdf", "excerpt": "exact text from the document", "relevance": "how this supports the answer"}}
  ]
}}

If you cannot find the answer in the documents, return:
{{"answer": "I couldn't find information about this in the provided documents.", "citations": []}}"""


def answer_question(question: str, documents_text: list[dict], client=None) -> dict:
    if client is None:
        client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)

    doc_text = ""
    for d in documents_text:
        chunks = chunk_text(d["text"], chunk_size=4000, overlap=300)
        for i, chunk in enumerate(chunks[:5]):
            doc_text += f"\n--- {d['filename']} (part {i+1}) ---\n{chunk}\n"
        if len(doc_text) > 35000:
            break

    try:
        resp = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are an M&A due diligence research analyst specializing in Indian M&A."},
                {"role": "user", "content": QA_PROMPT.format(
                    documents=doc_text, question=question
                )},
            ],
            temperature=0.1,
            max_tokens=2048,
        )
        content = resp.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        return json.loads(content)
    except Exception as e:
        return {
            "answer": f"Error: {str(e)}",
            "citations": [],
        }
