import nltk
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from logger import logger


try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")
    nltk.download("punkt_tab")


#Paragraph Chunking

## split long paragraphs if exceeds max chunk
def _split_long_paragraph(text : str,max_size: int)->list[str]:
    sentences = nltk.sent_tokenize(text)
    chunks=[]
    current=""

    for sentence in sentences:
        if len(current) + len(sentence) + 1 <=max_size:
            current +=" " + sentence
        else:
            if current.strip():
                chunks.append(current.strip())
            current = sentence
    if current.strip():
        chunks.append(current.strip())
    return chunks

# Paragraph splitting

def chunk_by_paragraph(
        text: str,
        min_chunk_size: int = 100,
        max_chunk_size: int = 800,
        overlap_sentences: int = 1
)-> list[dict]:
    raw_paragraph =text.split("\n\n")
    chunks = []
    previous_sentences = []

    for para in raw_paragraph:
        para= para.strip()
        sub_chunks = (_split_long_paragraph(para, max_chunk_size)
                      if len(para) > max_chunk_size else [para]) 

        for sub in sub_chunks:
            if len(previous_sentences) and overlap_sentences > 0:
                overlap=" ".join(previous_sentences[-overlap_sentences:])
                final_text =overlap +" "+sub 
            else :
                final_text=sub
            chunks.append({
                "text": final_text.strip(),
                "index":len(chunks),
                "char_count" : len(final_text.strip()),
                "strategy": "paragraph"
            })

    logger.info(f"Paragraph chunking produced {len(chunks)} chunks")
    return chunks

# Semantic Chunking

_embedding_model_cache = None

def _get_embedding_model(model_name: str):
    """Cache the model in memory — don't reload it every call."""
    global _embedding_model_cache
    if _embedding_model_cache is None:
        _embedding_model_cache = SentenceTransformer(model_name)
    return _embedding_model_cache


def chunk_by_semantic(
    text: str,
    model_name: str = "all-MiniLM-L6-v2",
    similarity_threshold: float = 0.2,   # ← tuned after running the model
    min_chunk_sentences: int = 2,
    overlap_sentences: int = 1
) -> list[dict]:
    model = _get_embedding_model(model_name)
    sentences = nltk.sent_tokenize(text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 15]

    if len(sentences) < 2:
        return [{"text": text.strip(), "index": 0,
                 "char_count": len(text.strip()), "sentence_count": len(sentences),
                 "strategy": "semantic"}]

    embeddings = model.encode(sentences, show_progress_bar=False)

    similarities = [
        cosine_similarity(embeddings[i].reshape(1, -1),
                           embeddings[i+1].reshape(1, -1))[0][0]
        for i in range(len(sentences) - 1)
    ]

    split_points = [0]
    for i, sim in enumerate(similarities):
        sentences_in_chunk = i + 1 - split_points[-1]
        if sim < similarity_threshold and sentences_in_chunk >= min_chunk_sentences:
            split_points.append(i + 1)
    split_points.append(len(sentences))

    chunks = []
    for i in range(len(split_points) - 1):
        start, end = split_points[i], split_points[i + 1]
        chunk_sentences = sentences[start:end]

        if i > 0 and overlap_sentences > 0:
            prev_start = split_points[i - 1]
            overlap = sentences[prev_start:start][-overlap_sentences:]
            chunk_sentences = overlap + chunk_sentences

        chunk_text = " ".join(chunk_sentences)
        chunks.append({
            "text": chunk_text.strip(),
            "index": len(chunks),
            "char_count": len(chunk_text.strip()),
            "sentence_count": end - start,
            "strategy": "semantic"
        })

    logger.info(f"Semantic chunking produced {len(chunks)} chunks "
                f"(threshold={similarity_threshold})")
    return chunks


###

def chunk_document(text: str, strategy: str = "paragraph", **kwargs) -> list[dict]:
    if strategy == "paragraph":
        return chunk_by_paragraph(text, **kwargs)
    elif strategy == "semantic":
        return chunk_by_semantic(text, **kwargs)
    else:
        raise ValueError(f"Unknown strategy: {strategy}")






    
