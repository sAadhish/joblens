import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'day73a_loaders'))

from chunker import chunk_by_paragraph, print_chunk_stats
from loaders import load_document

print()
print("=" * 55)
print("TEST 4 — Chunk Real Resume PDF")
print("=" * 55)

resume_path = "../day73a_loaders/sample.pdf"

if os.path.exists(resume_path):
    # Load PDF using our loader from Day 73a
    resume_text = load_document(resume_path)
    print(f"Resume loaded: {len(resume_text)} characters")

    # Chunk it
    resume_chunks = chunk_by_paragraph(resume_text)
    print_chunk_stats(resume_chunks)

    print("\nChunks from your resume:")
    for chunk in resume_chunks:
        print(f"\n  Chunk {chunk['index']} ({chunk['char_count']} chars):")
        print(f"  {chunk['text'][:150]}")
else:
    print(f"Resume not found at {resume_path}")
    print("Copy your sample.pdf here to test with real data")


