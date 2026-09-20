from fastapi import APIRouter, HTTPException
from api.schemas import ChatRequest, ChatResponse
from joblens_langchain.graphs.career_agent_graph import career_agent
import logging
import time
from api.cache import response_cache
from api.structured_logger import structured_logger


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    start_time = time.time()
    config = {"configurable": {"thread_id": request.session_id}}

    # Check if existing or new thread
    existing = career_agent.get_state(config)
    is_new = not existing.values

    # Cache check — only for new sessions
    # Existing sessions have conversation context that changes answers
    if is_new:
        cached = response_cache.get(request.message, request.session_id)
        if cached:
            latency = round(time.time() - start_time, 3)
            logger.info(f"[/chat] CACHE HIT latency={latency}s session={request.session_id}")
            return ChatResponse(**cached, session_id=request.session_id)

    # Build initial state based on new vs existing thread
    if is_new:
        initial_state = {
            "question": request.message,
            "source_label": None,
            "messages": [],
            "chat_history": [],
            "question_type": "",
            "classified_company": "",
            "original_question": request.message,
            "reformulated_question": request.message,
            "retrieved_chunks": [],
            "chunk_sources": [],
            "sources": [],
            "chunks_used": 0,
            "answer": "",
            "answer_quality": "",
            "iteration_count": 0,
            "max_iterations": 2,
            "error": None
        }
    else:
        initial_state = {
            "question": request.message,
            "original_question": request.message,
            "reformulated_question": request.message,
            "iteration_count": 0,
            "max_iterations": 2,
            "answer_quality": "",
            "answer": ""
        }

    try:
        final_state = None
        for state in career_agent.stream(
            initial_state,
            config=config,
            stream_mode="values"
        ):
            final_state = state

        if not final_state:
            raise HTTPException(status_code=500, detail="Agent returned no response")

        latency = round(time.time() - start_time, 3)
        structured_logger.log_request(
    endpoint="/chat",
    session_id=request.session_id,
    question=request.message,
    question_type=final_state.get("question_type", ""),
    latency_ms=round((time.time() - start_time) * 1000, 2),
    cache_hit=False,  # set True when cache hit
    iterations=final_state.get("iteration_count", 1),
    sources=final_state.get("sources", [])
)

        # Store in cache for new sessions only
        if is_new:
            cache_data = {
                "answer": final_state.get("answer", ""),
                "sources": final_state.get("sources", []),
                "question_type": final_state.get("question_type", ""),
                "iterations_used": final_state.get("iteration_count", 1),
            }
            response_cache.set(request.message, cache_data, request.session_id)

        return ChatResponse(
            answer=final_state.get("answer", "No answer generated"),
            sources=final_state.get("sources", []),
            question_type=final_state.get("question_type", ""),
            iterations_used=final_state.get("iteration_count", 1),
            session_id=request.session_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[/chat] failed: {e}")
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)[:200]}")




'''
from fastapi import APIRouter, HTTPException
from api.schemas import ChatRequest, ChatResponse
from joblens_langchain.graphs.career_agent_graph import career_agent
import logging
import time
from api.cache import response_cache


router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    start_time = time.time()

    config = {"configurable": {"thread_id": request.session_id}}


    try :
        final_state =None
        for state in career_agent.stream(
                        {
                        "question": request.message,
                        "original_question": request.message,
                        "reformulated_question": request.message,
                        "iteration_count": 0,
                        "max_iterations": 2,
                        "answer_quality": "",
                        "answer": "",
                        },
                        config=config,
                        stream_mode="values"
                    ):
               final_state=state

        if not final_state:
            raise HTTPException(status_code=500, detail="Agent returned no response")
        
        logger.info(
            f"[/chat] session={request.session_id} "
            f"type={final_state.get('question_type')} "
            f"iterations={final_state.get('iteration_count')}"
        )

        latency = round(time.time() - start_time, 3)
        logger.info(f"[/chat] latency={latency}s session={request.session_id}")

        

        return ChatResponse(
            answer=final_state.get("answer", "No answer generated"),
            sources=final_state.get("sources", []),
            question_type=final_state.get("question_type", ""),
            iterations_used=final_state.get("iteration_count", 1),
            session_id=request.session_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[/chat] failed: {e}")
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)[:200]}")



'''