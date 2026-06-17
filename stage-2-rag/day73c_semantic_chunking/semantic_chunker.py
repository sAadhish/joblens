# ===================================
# SEMANTIC CHUNKER
# Splits text when topic changes
# Uses embedding similarity to detect topic shifts
# ===================================

import nltk
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Download NLTK sentence tokenizer
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")
    nltk.download("punkt_tab")


# -------------------------------------------------------
# CORE — Semantic Chunker
# -------------------------------------------------------

def chunk_by_semantic(
    text: str,
    model_name: str = "all-MiniLM-L6-v2",
    similarity_threshold: float = 0.2,
    min_chunk_sentences: int = 2,
    overlap_sentences: int = 1
) -> list[dict]:
   

    # Step 1 — Load embedding model
    print(f"Loading embedding model: {model_name}")
    model = SentenceTransformer(model_name)

    # Step 2 — Split into sentences
    sentences = nltk.sent_tokenize(text)

    # Filter out very short sentences (noise)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 15]

    print(f"Document has {len(sentences)} sentences")

    # Handle edge case — too few sentences to chunk
    if len(sentences) < 2:
        return [{
            "text": text.strip(),
            "index": 0,
            "char_count": len(text.strip()),
            "sentence_count": len(sentences),
            "strategy": "semantic"
        }]

    # Step 3 — Embed ALL sentences at once
    # Doing it all at once is faster than one-by-one
    print("Embedding all sentences...")
    embeddings = model.encode(sentences, show_progress_bar=False)

    # Step 4 — Calculate similarity between adjacent sentences
    # Compare sentence[i] with sentence[i+1]
    similarities = []
    for i in range(len(sentences) - 1):
        sim = cosine_similarity(
            embeddings[i].reshape(1, -1),
            embeddings[i + 1].reshape(1, -1)
        )[0][0]
        similarities.append(sim)

    print(f"Similarity scores between adjacent sentences:")
    for i, sim in enumerate(similarities):
        marker = " ← SPLIT" if sim < similarity_threshold else ""
        print(f"  Sentence {i} → {i+1}: {sim:.3f}{marker}")

    # Step 5 — Find split points
    # A split happens where similarity drops below threshold
    split_points = [0]  

    for i, sim in enumerate(similarities):
        sentences_in_current_chunk = i + 1 - split_points[-1]

        # Only split if:
        # 1. Similarity is below threshold (topic changed)
        # 2. Current chunk has minimum required sentences
        if (sim < similarity_threshold and
                sentences_in_current_chunk >= min_chunk_sentences):
            split_points.append(i + 1)

    split_points.append(len(sentences))  # end of document

    print(f"\nSplit points found: {split_points}")
    print(f"Will create {len(split_points) - 1} chunks")

    # Step 6 — Build chunks from split points
    chunks = []

    for i in range(len(split_points) - 1):
        start = split_points[i]
        end = split_points[i + 1]

        # Get sentences for this chunk
        chunk_sentences = sentences[start:end]

        # Add overlap from previous chunk
        if i > 0 and overlap_sentences > 0:
            prev_start = split_points[i - 1]
            prev_sentences = sentences[prev_start:start]
            # Take last N sentences from previous chunk
            overlap = prev_sentences[-overlap_sentences:]
            chunk_sentences = overlap + chunk_sentences

        chunk_text = " ".join(chunk_sentences)

        chunks.append({
            "text": chunk_text.strip(),
            "index": len(chunks),
            "char_count": len(chunk_text.strip()),
            "sentence_count": end - start,
            "strategy": "semantic",
            "similarity_threshold": similarity_threshold
        })

    return chunks


# -------------------------------------------------------
# STATS — same as paragraph chunker
# -------------------------------------------------------

def print_chunk_stats(chunks: list[dict]) -> None:
    if not chunks:
        print("No chunks to analyze")
        return

    sizes = [c["char_count"] for c in chunks]

    print(f"\n--- Chunk Statistics ---")
    print(f"Total chunks      : {len(chunks)}")
    print(f"Smallest chunk    : {min(sizes)} chars")
    print(f"Largest chunk     : {max(sizes)} chars")
    print(f"Average size      : {sum(sizes) // len(sizes)} chars")
    print(f"Strategy          : semantic")
    print(f"Threshold used    : {chunks[0]['similarity_threshold']}")