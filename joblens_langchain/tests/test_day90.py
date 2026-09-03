import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graphs.career_agent_graph import career_agent
from langsmith_setup import setup_langsmith

setup_langsmith()


def ask(thread_id: str, question: str, max_iterations: int = 2):
    config={"configurable":{"thread_id":thread_id}}
    final_state=None

    
    for state in career_agent.stream(
        {
        "question": question,
        "original_question": question,
        "reformulated_question": question,
        "iteration_count": 0,
        "max_iterations": max_iterations,
        "answer_quality": "",
        "answer": "",
        },
        config=config,
        stream_mode="values"
    ):

        final_state=state
    return final_state


print("=" * 55)
print("TEST 1 — JD question: routes to jd_retrieve")
print("=" * 55)

r1 = ask("agent_001", "What does the Haptik AI Engineer role require?")
print(f"Classified as: {r1['question_type']} → company: {r1['classified_company']}")
print(f"Sources: {r1['sources']}")
print(f"Answer: {r1['answer'][:200]}")


print()
print("=" * 55)
print("TEST 2 — Resume question: routes to resume_retrieve")
print("=" * 55)

r2 = ask("agent_001", "What BI tools do I have experience with?")
print(f"Classified as: {r2['question_type']} → company: {r2['classified_company']}")
print(f"Sources: {r2['sources']}")
print(f"Answer: {r2['answer'][:200]}")


print()
print("=" * 55)
print("TEST 3 — Comparison: routes to general_retrieve")
print("=" * 55)

r3 = ask("agent_001", "Compare the Sarvam AI and Freshworks roles")
print(f"Classified as: {r3['question_type']} → company: {r3['classified_company']}")
print(f"Sources: {r3['sources']}")
print(f"Answer: {r3['answer'][:200]}")


print()
print("=" * 55)
print("TEST 4 — Multi-turn: uses conversation memory")
print("=" * 55)

r4 = ask("agent_002", "What does the Freshworks Data Analyst role need?")
print(f"Turn 1: {r4['answer'][:150]}")

r5 = ask("agent_002", "Do I have the skills for that role based on my background?")
print(f"Turn 2: {r5['answer'][:200]}")
print(f"(Should reference both Freshworks JD from turn 1 AND resume)")


