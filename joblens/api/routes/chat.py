from fastapi import APIRouter, HTTPException
from api.schemas import ChatRequest, ChatResponse
from joblens_langchain.graphs.career_agent_graph import career_agent
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

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



