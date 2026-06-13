import json
from openai import OpenAI
from app.config import settings
from app.services.chunking import chunk_text

QA_PROMPT = """You are an M&A due diligence Q&A assistant. Answer the question based SOLELY on the provided document excerpts.

If the answer cannot be found, say "I couldn't find information about this in the provided documents."

Documents:
{documents}

Question: {question}

Return a JSON object:
{{
  "answer": "your detailed answer",
  "citations": [
    {{"filename": "doc1.pdf", "excerpt": "relevant text", "relevance": "why relevant"}}
  ]
}}

Only return valid JSON. No markdown fences."""


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
