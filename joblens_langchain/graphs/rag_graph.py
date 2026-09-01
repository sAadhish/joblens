from langgraph.graph import StateGraph, START, END
from graphs.state import RAGState
from graphs.nodes import retrieve_node, generate_node , evaluate_node,reformulate_node
from logger import logger



def should_continue(state: RAGState):

    quality = state.get("answer_quality", "good")
    iteration = state.get("iteration_count", 0)
    max_iter = state.get("max_iterations", 3)

    if quality == "bad" and iteration<max_iter:
        logger.info(f"[should_continue] routing to reformulate (iteration {iteration})")
        return "reformulate"
    else:
        logger.info(f"[should_continue] routing to END (quality={quality})")
        return "end"


def build_rag_graph():
  
    graph = StateGraph(RAGState)


    graph.add_node("retrieve", retrieve_node)
    graph.add_node("generate", generate_node)
    graph.add_node("evaluate",evaluate_node)
    graph.add_node("reformulate",reformulate_node)


    graph.add_edge(START, "retrieve")     
    graph.add_edge("retrieve", "generate") 
    graph.add_edge("generate", "evaluate")      
    graph.add_edge("reformulate","retrieve")  

    graph.add_conditional_edges(
        "evaluate",
        should_continue,
        {
            "reformulate":"reformulate",
            "end":END
        }
    )

    compiled = graph.compile()

    logger.info("Self-correcting RAG graph compiled")
    return compiled

rag_graph = build_rag_graph()




