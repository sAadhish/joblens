from langgraph.graph import START,END,StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage,AIMessage
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from graphs.state import ConversationState
from vectorstore.qdrant_service import QdrantService
from services.llm_service import LLMService
from config import Config
from logger import logger

_vector_service = None
_llm =None

def _get_services():
    global _vector_service,_llm
    if _vector_service is None:
        _vector_service=QdrantService()
    if _llm is None:
        _llm=LLMService.get_model()
    return _vector_service,_llm


def retrieve_node(state:ConversationState) ->dict:
    _vector_service,_= _get_services()
    question = state["question"]
    source_label =state.get("source_label")
    chunks=_vector_service.retrieve(
        question=question,
        source_label=source_label,
        top_k=Config.RETRIEVAL_TOP_K
    )
    logger.info(f"[conv_retrieve] found {len(chunks)} chunks for '{question[:40]}'")

    return{
        "retrieved_chunks" :[c.text for c in chunks],
        "chunk_sources": [c.source_label for c in chunks],
        "sources": list({c.source_label for c in chunks}),
        "chunks_used": len(chunks)
    }



def load_history_node(state: ConversationState) -> dict:

    messages = state.get("messages", [])
    logger.info(f"[load_history_node] loaded {len(messages)} messages from history")
    return {"chat_history": messages}


def generate_node(state: ConversationState)-> dict:
    _,_llm=_get_services()

    chunks= state["retrieved_chunks"]
    question=state["question"]
    chat_history = state.get("chat_history", [])

    context_parts=[]
    chunk_sources = state.get("chunk_sources", [])
    for i,chunk in enumerate(chunks,1):
        source=chunk_sources[i-1] if i<= len(chunk_sources) else "unknown"
        context_parts.append(f"[Source {i}: {source}]\{chunk}")
    context = "\n\n".join(context_parts) if context_parts else "No relevant documents found."

    # Prompt with conversation history injected
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a career advisor for tech professionals in India.
Answer using ONLY the provided documents.
If the answer is not in the documents, say "I don't have enough information to answer that."
Do not use general knowledge. Cite sources like [Source 1: Company JD].

DOCUMENTS:
{context}"""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}")
    ])

    chain = prompt | _llm | StrOutputParser()

    recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history

    try:
        answer = chain.invoke({
            "context": context,
            "chat_history": recent_history,
            "question": question
        })
        logger.info(f"[conv_generate] answer: {len(answer)} chars | history: {len(chat_history)} messages")
    except Exception as e:
        logger.error(f"[conv_generate] failed: {e}")
        answer = "I encountered an error. Please try again."

   
    new_messages = [
        HumanMessage(content=question),
        AIMessage(content=answer)
    ]

    return {
        "answer": answer,
        "messages": new_messages,  
        "error": None
    }


# -------------------------------------------------------
# GRAPH ASSEMBLY
# -------------------------------------------------------

def build_conversation_graph():
  
    graph = StateGraph(
                       ConversationState,
                       input=ConversationState,
                       output=ConversationState
                       )
    
    graph.add_node("load_history", load_history_node) 
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("generate", generate_node)

    graph.add_edge(START, "load_history")              
    graph.add_edge("load_history", "retrieve")          
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)

    
    checkpointer = MemorySaver()


    compiled = graph.compile(checkpointer=checkpointer)
    logger.info("Conversation graph compiled with MemorySaver checkpointer")
    return compiled


conversation_graph = build_conversation_graph()