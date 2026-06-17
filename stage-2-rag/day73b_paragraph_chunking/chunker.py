# ===================================
# PARAGRAPH CHUNKER
# Splits documents at natural paragraph boundaries
# Fast, simple, no ML model needed
# ===================================

import re
import nltk

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")
    nltk.download("punkt_tab")


# -------------------------------------------------------
# Split long paragraphs
# -------------------------------------------------------

def split_long_paragraph(text: str, max_size: int) -> list[str]:

    sentences = nltk.sent_tokenize(text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= max_size:
            current_chunk += " " + sentence
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = sentence

    # Don't forget the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


# -------------------------------------------------------
# MAIN — Paragraph Chunker
# -------------------------------------------------------

def chunk_by_paragraph(
    text: str,
    min_chunk_size: int = 100,
    max_chunk_size: int = 1000,
    overlap_sentences: int = 1
) -> list[dict]:
    

    raw_paragraphs = text.split("\n\n")

    chunks = []
    previous_sentences = []  

    for para in raw_paragraphs:
        para = para.strip()

        if not para:
            continue
        if len(para) < min_chunk_size:
            continue

        if len(para) > max_chunk_size:
            sub_chunks = split_long_paragraph(para, max_chunk_size)
        else:
            sub_chunks = [para]

        #Add overlap + store each chunk
        for sub in sub_chunks:

            if previous_sentences and overlap_sentences > 0:
                overlap_text = " ".join(
                    previous_sentences[-overlap_sentences:]
                )
                final_text = overlap_text + " " + sub
            else:
                final_text = sub

            chunks.append({
                "text": final_text.strip(),
                "index": len(chunks),
                "char_count": len(final_text.strip()),
                "strategy": "paragraph"
            })

            # Update overlap buffer with this chunk's sentences
            previous_sentences = nltk.sent_tokenize(sub)

    return chunks


# -------------------------------------------------------
# STATS — understand your chunks before using them
# -------------------------------------------------------

def print_chunk_stats(chunks: list[dict]) -> None:
    

    if not chunks:
        print("No chunks to analyze")
        return

    sizes = [c["char_count"] for c in chunks]

    print(f"\n--- Chunk Statistics ---")
    print(f"Total chunks    : {len(chunks)}")
    print(f"Smallest chunk  : {min(sizes)} chars")
    print(f"Largest chunk   : {max(sizes)} chars")
    print(f"Average size    : {sum(sizes) // len(sizes)} chars")
    print(f"Total content   : {sum(sizes)} chars")




