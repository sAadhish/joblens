import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graphs.rag_graph import rag_graph
from langsmith_setup import setup_langsmith

setup_langsmith()


def run_query(question: str, source_label: str = None):
    """Run one query through the graph and print results."""

    
    result = rag_graph.invoke({
        "question": question,
        "source_label": source_label,
        "retrieved_chunks": [],
        "retrieval_scores": [],
        "answer": "",
        "sources": [],
        "chunks_used": 0,
        "error": None
    })
    return result


print("=" * 55)
print("TEST 1 — Basic graph invocation")
print("=" * 55)

result = run_query(
    "What does the Sarvam AI role require?",
    source_label="Sarvam AI JD"
)

print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources']}")
print(f"Chunks used: {result['chunks_used']}")
print(f"Retrieval scores: {result['retrieval_scores']}")


print()
print("=" * 55)
print("TEST 2 — Stream mode (see each node as it completes)")
print("=" * 55)

print("\nStreaming graph execution:\n")
for step in rag_graph.stream({
    "question": "What experience level does the Freshworks role need?",
    "source_label": "Freshworks JD",
    "retrieved_chunks": [],
    "retrieval_scores": [],
    "answer": "",
    "sources": [],
    "chunks_used": 0,
    "error": None
}):

    node_name = list(step.keys())[0]
    updates = step[node_name]
    print(f"Node '{node_name}' completed:")
    for key, value in updates.items():
        if isinstance(value, str):
            print(f"  {key}: {value[:80]}")
        else:
            print(f"  {key}: {value}")
    print()


print("=" * 55)
print("TEST 3 — No source filter (searches all documents)")
print("=" * 55)

result = run_query("Does any role require Kubernetes?")
print(f"Answer: {result['answer']}")
print(f"Sources consulted: {result['sources']}")