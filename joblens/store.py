from config import embedding_model, collection
import hashlib
from logger import logger
from rag import index_document #for connecting to rag
import tempfile #for connecting to rag
import os




def clean_field(value, fallback):
    """Handle None, empty string, and all 'not specified' variations from LLM."""
    if value is None:
        return fallback
    if str(value).strip().lower() in ["not specified", "not specified in jd", "n/a", "none", ""]:
        return fallback
    return value


def store_jd(jd_text: str, company: str, structured: dict) -> str:

    if not structured:
        logger.error(f"Skkiping store_jd for {company} - because no structured data")
        return None
    
    try:
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

        collection.add(
            documents=[jd_text],
            embeddings=embeddings,
            metadatas=[metadata],
            ids=[doc_id]
        )
        logger.info(f"JD stored — company: {company} | role: {metadata['role']}")

        # Need to connect this stage to Rag --- for this we need to add this jd_text to chunker in rag and connect using 
        # same source name 
        #########
        source_label = f"{company} JD"

        with tempfile.NamedTemporaryFile(mode="w",suffix=".txt",delete=False) as tmp:
            tmp.write(jd_text)
            tmp_path=tmp.name

        index_document(tmp_path,source_label, strategy="paragraph")

        os.remove(tmp_path)
        #########
        return doc_id
    
    except Exception as e:
        logger.error(f"Failed to store JD for {company}: {e}")
        return None

