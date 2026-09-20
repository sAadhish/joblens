import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graphs.conversation_graph import conversation_graph
from langsmith_setup import setup_langsmith

setup_langsmith()


def chat(thread_id: str, question: str, source_label: str = None):
  
    config = {"configurable": {"thread_id": thread_id}}
    final_state= None

    for state in conversation_graph.stream(
        {
            "question": question,
            "source_label": source_label
            
        },
        config=config  ,
        stream_mode="values"
    ): 
        final_state=state

    return final_state


# -------------------------------------------------------
# TEST 1 — Multi-turn conversation
# Turn 2 uses vague reference ("that role") — needs memory
# -------------------------------------------------------
print("=" * 55)
print("TEST 1 — Multi-turn: vague references need memory")
print("=" * 55)

THREAD = "test_session_001"

# Turn 1 — establish context
r1 = chat(THREAD, "What does the Sarvam AI role require?", "Sarvam AI JD")
print(f"\nTurn 1 Q: What does the Sarvam AI role require?")
print(f"Turn 1 A: {r1['answer'][:150]}")
print(f"messagess in history: {len(r1['messages'])}")

# Turn 2 — "that role" refers to Sarvam AI from Turn 1
r2 = chat(THREAD, "How many years of experience does that role need?", "Sarvam AI JD")
print(f"\nTurn 2 Q: How many years of experience does that role need?")
print(f"Turn 2 A: {r2['answer'][:150]}")
print(f"messagess in history: {len(r2['messages'])}")

# Turn 3 — "Is that a lot" refers to the years from Turn 2
r3 = chat(THREAD, "What tech stack should I learn to qualify?", "Sarvam AI JD")
print(f"\nTurn 3 Q: What tech stack should I learn to qualify?")
print(f"Turn 3 A: {r3['answer'][:150]}")
print(f"messagess in history: {len(r3['messages'])}")


# -------------------------------------------------------
# TEST 2 — Different thread = fresh conversation
# Proves threads are completely isolated
# -------------------------------------------------------
print()
print("=" * 55)
print("TEST 2 — New thread = fresh start (no memory of Test 1)")
print("=" * 55)

NEW_THREAD = "test_session_002"  # different thread_id

r4 = chat(NEW_THREAD, "What tech stack should I learn to qualify?", "Sarvam AI JD")
print(f"\nQ: What tech stack should I learn to qualify?")
print(f"A: {r4['answer'][:150]}")
print(f"messagess in history: {len(r4['messages'])}")
print("\n(Should ask 'qualify for what?' or give generic answer —")
print(" because this thread has no memory of the Sarvam AI context)")


# -------------------------------------------------------
# TEST 3 — Same thread resumed after "session"
# Proves checkpointer persists within process lifetime
# -------------------------------------------------------
print()
print("=" * 55)
print("TEST 3 — Resume same thread (session continuity)")
print("=" * 55)

# Going back to THREAD from Test 1 — it still remembers
r5 = chat(THREAD, "Summarize what we discussed about Sarvam AI", "Sarvam AI JD")
print(f"\nQ: Summarize what we discussed about Sarvam AI")
print(f"A: {r5['answer'][:200]}")
print(f"Total messagess in history: {len(r5['messages'])}")
print("\n(Should reference all 3 previous turns from Test 1)")