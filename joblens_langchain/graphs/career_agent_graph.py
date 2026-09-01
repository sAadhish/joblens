# ===================================
# CAREER AGENT GRAPH
# Complete JobLens agent — routing + memory + self-correction
# ===================================

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from graphs.state import AgentState
from graphs.nodes import (
    agent_load_history,
    classify_node,
    jd_retrieve_node,
    resume_retrieve_node,
    general_retrieve_node,
    agent_generate_node,
    agent_evaluate_node,
    agent_reformulate_node
)
from logger import logger


# -------------------------------------------------------
# ROUTING FUNCTIONS — conditional edges
# -------------------------------------------------------

def route_by_type(state: AgentState) -> str:
    """
    Called after classify_node.
    Routes to the right retrieval node based on question type.
    """
    q_type = state.get("question_type", "general")

    routes = {
        "jd": "jd_retrieve",
        "resume": "resume_retrieve",
        "comparison": "general_retrieve",
        "general": "general_retrieve"
    }

    route = routes.get(q_type, "general_retrieve")
    logger.info(f"[route_by_type] {q_type} → {route}")
    return route


def should_continue(state: AgentState) -> str:
    """Called after evaluate_node."""
    quality = state.get("answer_quality", "good")
    iteration = state.get("iteration_count", 0)
    max_iter = state.get("max_iterations", 2)

    if quality == "bad" and iteration < max_iter:
        return "reformulate"
    return "end"


# -------------------------------------------------------
# GRAPH ASSEMBLY
# -------------------------------------------------------

def build_career_agent():
    graph = StateGraph(AgentState)

    # Add all nodes
    graph.add_node("load_history", agent_load_history)
    graph.add_node("classify", classify_node)
    graph.add_node("jd_retrieve", jd_retrieve_node)
    graph.add_node("resume_retrieve", resume_retrieve_node)
    graph.add_node("general_retrieve", general_retrieve_node)
    graph.add_node("generate", agent_generate_node)
    graph.add_node("evaluate", agent_evaluate_node)
    graph.add_node("reformulate", agent_reformulate_node)

    # Fixed edges
    graph.add_edge(START, "load_history")
    graph.add_edge("load_history", "classify")

    # Conditional routing after classify
    graph.add_conditional_edges(
        "classify",
        route_by_type,
        {
            "jd_retrieve": "jd_retrieve",
            "resume_retrieve": "resume_retrieve",
            "general_retrieve": "general_retrieve"
        }
    )

    # All retrieve nodes flow into generate
    graph.add_edge("jd_retrieve", "generate")
    graph.add_edge("resume_retrieve", "generate")
    graph.add_edge("general_retrieve", "generate")
    graph.add_edge("generate", "evaluate")

    # Conditional after evaluate
    graph.add_conditional_edges(
        "evaluate",
        should_continue,
        {
            "reformulate": "reformulate",
            "end": END
        }
    )

    # After reformulate — re-classify to route correctly again
    graph.add_edge("reformulate", "classify")

    checkpointer = MemorySaver()
    compiled = graph.compile(checkpointer=checkpointer)
    logger.info("Career agent compiled: routing + memory + self-correction")
    return compiled


career_agent = build_career_agent()