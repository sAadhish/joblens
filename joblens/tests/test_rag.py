# ===================================
# TEST — Full RAG Pipeline
# ===================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag import index_document, rag_query


print("=" * 55)
print("STEP 1 — Indexing documents")
print("=" * 55)
'''
# Index your actual resume
resume_path = os.path.join(os.path.dirname(__file__), "..", "sample.pdf")
if os.path.exists(resume_path):
    count = index_document(resume_path, "My Resume", strategy="semantic", similarity_threshold=0.25)
    print(f"✓ Resume indexed: {count} chunks")
else:
    print("⚠ sample.pdf not found — skipping resume indexing")

    '''

# Index a sample JD
jd_text_path = os.path.join(os.path.dirname(__file__), "..", "sample_jd.txt")
with open(jd_text_path, "w") as f:
    f.write("""Sarvam AI is looking for a Backend Engineer.

Requirements:
Strong Python and FastAPI experience is mandatory.
Must know gRPC and PostgreSQL deeply.
Docker and Kubernetes experience required.
Minimum 3 years of backend engineering experience.

Nice to Have:
Experience with Redis or Kafka.
Cloud experience on AWS or GCP.

About the Company:
Sarvam AI is building AI for India.
We work on speech, language, and multimodal AI systems.""")

count = index_document(jd_text_path, "Sarvam AI JD", strategy="paragraph")
print(f"✓ Sarvam AI JD indexed: {count} chunks")


print()
print("=" * 55)
print("STEP 2 — Asking real questions")
print("=" * 55)

questions = [
    "What does the Sarvam AI Backend Engineer role require?",
    "Does Sarvam AI offer remote work?",
    "What experience does my resume show in BI development?",
    "What is the capital of France?",  # should trigger "I don't have enough information"
]

for q in questions:
    print(f"\nQ: {q}")
    result = rag_query(q, top_k=3)
    print(f"A: {result['answers']}")
    print(f"   (sources: {result['sources']}, Chunks used: {result['chunks_used']})")