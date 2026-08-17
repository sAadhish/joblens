import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graphs.rag_graph import rag_graph
from langsmith_setup import setup_langsmith

setup_langsmith()


def run_query(question: str, source_label: str = None, max_iterations: int = 3):
    return rag_graph.invoke({
        "question": question,
        "source_label": source_label,
        "original_question": question,
        "reformulated_question": question,
        "retrieved_chunks": [],
        "retrieval_scores": [],
        "chunk_sources": [],
        "sources": [],
        "chunks_used": 0,
        "answer": "",
        "answer_quality": "",
        "error": None,
        "iteration_count": 0,
        "max_iterations": max_iterations
    })


# -------------------------------------------------------
# TEST 1 — Good retrieval: should end in one iteration
# -------------------------------------------------------
print("=" * 55)
print("TEST 1 — Question with good retrieval (expect 1 iteration)")
print("=" * 55)

result = run_query(
    "What Python frameworks does Sarvam AI require?",
    source_label="Sarvam AI JD"
)
print(f"Answer: {result['answer'][:150]}")
print(f"Iterations: {result['iteration_count']}")
print(f"Final quality: {result['answer_quality']}")


# -------------------------------------------------------
# TEST 2 — Bad source filter: forces retry loop
# Ask about a source that doesn't have this info
# Should trigger reformulation
# -------------------------------------------------------
print()
print("=" * 55)
print("TEST 2 — Poor retrieval (expect retry + reformulation)")
print("=" * 55)

result = run_query(
    "What is the annual bonus structure?",  # not in any JD
    source_label="Sarvam AI JD",
    max_iterations=2
)
print(f"Answer: {result['answer'][:150]}")
print(f"Iterations used: {result['iteration_count']}")
print(f"Original question: {result['original_question']}")
print(f"Final query used: {result['reformulated_question']}")


# -------------------------------------------------------
# TEST 3 — Stream: watch the retry loop happen in real time
# -------------------------------------------------------
print()
print("=" * 55)
print("TEST 3 — Stream mode: watch the graph decide")
print("=" * 55)

for step in rag_graph.stream({
    "question": "What is the stock option vesting schedule?",  # not in JDs
    "source_label": "Freshworks JD",
    "original_question": "What is the stock option vesting schedule?",
    "reformulated_question": "What is the stock option vesting schedule?",
    "retrieved_chunks": [],
    "retrieval_scores": [],
    "chunk_sources": [],
    "sources": [],
    "chunks_used": 0,
    "answer": "",
    "answer_quality": "",
    "error": None,
    "iteration_count": 0,
    "max_iterations": 2
}):
    node_name = list(step.keys())[0]
    updates = step[node_name]
    print(f"\n→ Node '{node_name}' completed:")

    # Print only the interesting updates
    interesting = ["answer_quality", "iteration_count",
                   "reformulated_question", "chunks_used"]
    for key in interesting:
        if key in updates:
            print(f"   {key}: {updates[key]}")
    if "answer" in updates and updates["answer"]:
        print(f"   answer: {updates['answer'][:80]}")