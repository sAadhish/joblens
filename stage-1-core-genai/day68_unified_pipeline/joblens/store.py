# ===================================
# MODULE 2 — JD STORE
# Embeds and stores JD in vector DB
# ===================================
from config import embedding_model, collection
import hashlib


def clean_field(value, fallback):
    """Handle None, empty string, and all 'not specified' variations from LLM."""
    if value is None:
        return fallback
    if str(value).strip().lower() in ["not specified", "not specified in jd", "n/a", "none", ""]:
        return fallback
    return value


def store_jd(jd_text: str, company: str, structured: dict) -> str:

    embeddings = embedding_model.encode([jd_text]).tolist()

    metadata = {
        "company": company,
        "role": clean_field(structured.get("role"), "unknown"),
        "company_type": clean_field(structured.get("company_type"), "unknown"),
        "role_type": clean_field(structured.get("role_type"), "unknown"),
        "experience_min": structured.get("experience_min") or 0,
        "experience_max": structured.get("experience_max") or 10,
        "location": clean_field(structured.get("location"), "India"),
        "remote_ok": clean_field(structured.get("remote_ok"), False),
        
    }

    doc_id = hashlib.md5(jd_text.encode()).hexdigest()

    try:
        collection.add(
            documents=[jd_text],
            embeddings=embeddings,
            metadatas=[metadata],
            ids=[doc_id]
        )
        return doc_id
    except Exception:
        return doc_id
    

