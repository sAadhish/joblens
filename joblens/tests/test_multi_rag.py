import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stage2_rag.rag import index_document, compare_sources

# Index a second JD for real comparison
haptik_jd_path = os.path.join(os.path.dirname(__file__), "..", "haptik_jd.txt")
with open(haptik_jd_path, "w") as f:
    f.write("""Haptik is looking for an AI Engineer.

Requirements:
Python and NLP experience required.
LangChain and vector database experience preferred.
RAG system experience is a strong plus.
1-3 years experience required.

About the Company:
Haptik builds conversational AI products for enterprises.""")

index_document(haptik_jd_path, "Haptik JD", strategy="paragraph")

print("=" * 55)
print("TEST — Multi-Document Comparison")
print("=" * 55)

question = "Compare the Sarvam AI and Haptik roles for my background"
result = compare_sources(question, source_label=["Sarvam AI JD", "Haptik JD"], per_source_k=2)

print(f"\nQ: {question}")
print(f"A: {result['answers']}")
print(f"\nSources used: {result['sources']} | Chunks: {result['chunks_used']}")