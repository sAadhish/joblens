# ===================================
# TEST — Ingestion Pipeline (Loaders + Chunkers)
# ===================================

import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stage2_rag.ingestion import load_document, chunk_document


def test_load_and_chunk_text():
    sample_text = """Sarvam AI is looking for a Backend Engineer.

Requirements:
Strong Python and FastAPI experience.
Knowledge of distributed systems.

About us:
Sarvam AI builds AI for India."""
    sample_path = os.path.join(os.path.dirname(__file__), "..", "sample_jd.txt")

    with open(sample_path, "w") as f:
        f.write(sample_text)

    text = load_document(sample_path)
    assert len(text) > 0

    chunks = chunk_document(text, strategy="paragraph")
    assert len(chunks) > 0
    print(f"✓ Text + paragraph chunking: {len(chunks)} chunks")

'''
def test_resume_pdf_semantic():
    resume_path = os.path.join(os.path.dirname(__file__), "..", "sample.pdf")
    if not os.path.exists(resume_path):
        print("⚠ sample.pdf not found — skipping resume test")
        return

    text = load_document(resume_path)
    chunks = chunk_document(text, strategy="semantic", similarity_threshold=0.25)
    assert len(chunks) > 0
    print(f"✓ Resume + semantic chunking: {len(chunks)} chunks")
'''

def test_strategy_comparison():
    text = """Sarvam AI is looking for a Backend Engineer.

Requirements:
Strong Python and FastAPI experience.
Must know gRPC and PostgreSQL.

Benefits:
Health insurance and equity.
Flexible working hours."""

    para = chunk_document(text, strategy="paragraph")
    sem = chunk_document(text, strategy="semantic", similarity_threshold=0.25)

    print(f"✓ Paragraph: {len(para)} chunks | Semantic: {len(sem)} chunks")


if __name__ == "__main__":
    test_load_and_chunk_text()
    #test_resume_pdf_semantic()
    test_strategy_comparison()
    print("\nAll ingestion tests completed.")