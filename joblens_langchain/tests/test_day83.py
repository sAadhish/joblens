import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.career_service import CareerService
from services.memory_rag_service import MemoryRAGService

service = CareerService()
memory_rag = MemoryRAGService(service.vector)


# -------------------------------------------------------
# TEST 1 — Callbacks: verify latency and cost are logged
# -------------------------------------------------------
print("=" * 55)
print("TEST 1 — Callbacks (check logs for latency + cost)")
print("=" * 55)

result = service.rag.query(
    question="What does the Sarvam AI role require?",
    source_label="Sarvam AI JD"
)
print(f"Answer: {result.answer[:100]}")
print("(Check logs above for Chain completed + latency + cost)")


# -------------------------------------------------------
# TEST 2 — Memory: multi-turn conversation
# The second question uses "that role" — needs memory to resolve
# -------------------------------------------------------
print()
print("=" * 55)
print("TEST 2 — Memory: multi-turn conversation")
print("=" * 55)

# Turn 1
r1 = memory_rag.chat(
    "What does the Sarvam AI role require?",
    source_label="Sarvam AI JD"
)
print(f"Turn 1 Q: What does the Sarvam AI role require?")
print(f"Turn 1 A: {r1.answer[:150]}")

# Turn 2 — "that role" refers to Sarvam AI from Turn 1
r2 = memory_rag.chat(
    "How many years of experience does that role need?",
    source_label="Sarvam AI JD"
)
print(f"\nTurn 2 Q: How many years of experience does that role need?")
print(f"Turn 2 A: {r2.answer[:150]}")

# Turn 3 — References previous answer
r3 = memory_rag.chat(
    "Is that a lot compared to typical backend roles?",
    source_label="Sarvam AI JD"
)
print(f"\nTurn 3 Q: Is that a lot compared to typical backend roles?")
print(f"Turn 3 A: {r3.answer[:150]}")

print(f"\nConversation history length: {len(memory_rag.get_history())} messages")


# -------------------------------------------------------
# TEST 3 — Memory reset
# After reset, context from previous turns is gone
# -------------------------------------------------------
print()
print("=" * 55)
print("TEST 3 — Memory reset")
print("=" * 55)

memory_rag.reset_memory()
r4 = memory_rag.chat(
    "How many years of experience does that role need?",
    source_label="Sarvam AI JD"
)
print(f"After reset Q: How many years of experience does that role need?")
print(f"After reset A: {r4.answer[:150]}")
print("(Should struggle with 'that role' — memory was cleared)")