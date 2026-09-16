
import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from graphs.career_agent_graph import career_agent, build_career_agent
from langsmith_setup import setup_langsmith
from logger import logger
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)


def run_career_assistant():
    """
    Interactive career assistant CLI.
    Runs the full LangGraph career agent with persistent memory.
    Type 'quit' to exit, 'new' to start a new session.
    """
    setup_langsmith()

    print()
    print("=" * 60)
    print("   JOBLENS — AI Career Assistant")
    print("=" * 60)
    print("   Ask me about job requirements, skill gaps,")
    print("   resume analysis, or career advice.")
    print("   Type 'new' for a new session | 'quit' to exit")
    print("=" * 60)
    print()

    session_count = 0
    thread_id = f"cli_session_{session_count}"

    # Check existing state
    config = {"configurable": {"thread_id": thread_id}}

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("Goodbye!")
            break

        if user_input.lower() == "new":
            session_count += 1
            thread_id = f"cli_session_{session_count}"
            config = {"configurable": {"thread_id": thread_id}}
            print(f"\n[New session started — Session {session_count}]\n")
            continue

        for state in career_agent.stream(
                {
                "question": user_input,
                "original_question": user_input,
                "reformulated_question": user_input,
                "iteration_count": 0,
                "max_iterations": 2,
                "answer_quality": "",
                "answer": "",
                },
                config=config,
                stream_mode="values"
            ):
        
                final_state=state


        if final_state:
            answer = final_state.get("answer", "I could not generate an answer.")
            q_type = final_state.get("question_type", "")
            sources = final_state.get("sources", [])
            iterations = final_state.get("iteration_count", 1)

            print(f"\nAssistant: {answer}")
            if sources:
                print(f"\n[Sources: {', '.join(sources)} | Type: {q_type} | Iterations: {iterations}]")
            print()


if __name__ == "__main__":
    run_career_assistant()