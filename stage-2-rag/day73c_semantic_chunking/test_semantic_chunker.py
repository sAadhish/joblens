# ===================================
# TEST — Semantic Chunking
# ===================================

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__),
                             '..', 'day73a_loaders'))
sys.path.append(os.path.join(os.path.dirname(__file__),
                             '..', 'day73b_paragraph_chunking'))

from semantic_chunker import chunk_by_semantic, print_chunk_stats
from chunker import chunk_by_paragraph
from loaders import load_document


# -------------------------------------------------------
# Test 1 — Basic semantic chunking
# Use a JD where topics change clearly
# Watch the similarity scores print
# -------------------------------------------------------

print("=" * 55)
print("TEST 1 — Basic Semantic Chunking")
print("=" * 55)

sample_jd = """Sarvam AI is looking for a Backend Engineer.
We need someone who can build low-latency APIs for ML models at scale.
Our systems handle millions of requests every single day.
Strong Python and FastAPI experience is mandatory.
You must know gRPC and PostgreSQL deeply.
Docker and Kubernetes experience required.
We offer competitive salary and equity to all employees.
Health insurance for you and your entire family.
Flexible working hours and remote friendly environment.
Learning budget of fifty thousand rupees per year.
Sarvam AI is building AI for India.
We work on speech, language, and multimodal AI systems.
Our team is small, fast-moving, and deeply technical."""

chunks = chunk_by_semantic(sample_jd, similarity_threshold=0.4)

print(f"\nChunks created:\n")
for chunk in chunks:
    print(f"Chunk {chunk['index']} "
          f"({chunk['sentence_count']} sentences, "
          f"{chunk['char_count']} chars):")
    print(f"  {chunk['text'][:200]}")
    print()

print_chunk_stats(chunks)


# -------------------------------------------------------
# Test 2 — Threshold tuning
# This is the most important test
# See how different thresholds change chunk count
# -------------------------------------------------------

print()
print("=" * 55)
print("TEST 2 — Threshold Tuning")
print("=" * 55)

thresholds = [0.2, 0.35, 0.5, 0.7]

print(f"\n{'Threshold':<12} {'Chunks':<10} {'Avg Size':<12}")
print("-" * 35)

for threshold in thresholds:
    chunks = chunk_by_semantic(
        sample_jd,
        similarity_threshold=threshold,
        min_chunk_sentences=1
    )
    sizes = [c["char_count"] for c in chunks]
    avg = sum(sizes) // len(sizes) if sizes else 0
    print(f"{threshold:<12} {len(chunks):<10} {avg:<12} chars")


# -------------------------------------------------------
# Test 3 — Semantic vs Paragraph on same document
# The comparison that matters most
# -------------------------------------------------------

print()
print("=" * 55)
print("TEST 3 — Semantic vs Paragraph Comparison")
print("=" * 55)

semantic_chunks = chunk_by_semantic(sample_jd, similarity_threshold=0.4)
paragraph_chunks = chunk_by_paragraph(sample_jd)

print(f"\nSemantic chunking  : {len(semantic_chunks)} chunks")
for c in semantic_chunks:
    print(f"  Chunk {c['index']}: {c['char_count']} chars "
          f"| {c['sentence_count']} sentences")

print(f"\nParagraph chunking : {len(paragraph_chunks)} chunks")
for c in paragraph_chunks:
    print(f"  Chunk {c['index']}: {c['char_count']} chars")




# -------------------------------------------------------
# Test 4 — Semantic chunking on your resume PDF
# Resume has inconsistent formatting → semantic wins here
# -------------------------------------------------------

print()
print("=" * 55)
print("TEST 4 — Semantic Chunking on Resume PDF")
print("=" * 55)

resume_path = "../day73a_loaders/sample.pdf"

if os.path.exists(resume_path):
    resume_text = load_document(resume_path)
    print(f"Resume loaded: {len(resume_text)} characters\n")

    # Semantic chunks
    sem_chunks = chunk_by_semantic(
        resume_text,
        similarity_threshold=0.35
    )
    print_chunk_stats(sem_chunks)

    print("\nSemantic chunks from resume:")
    for chunk in sem_chunks:
        print(f"\n  Chunk {chunk['index']} "
              f"({chunk['sentence_count']} sentences):")
        print(f"  {chunk['text'][:200]}")

    # Compare with paragraph chunks
    para_chunks = chunk_by_paragraph(resume_text)
    print(f"\nComparison:")
    print(f"  Semantic  : {len(sem_chunks)} chunks")
    print(f"  Paragraph : {len(para_chunks)} chunks")
else:
    print("Resume PDF not found — skipping")




