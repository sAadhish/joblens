import re
from stage2_rag.rag import rag_query, retrieve_chunks
from config import groq_client
from logger import logger

# Stage 1 - Retrival Quality
# Hit Hit Rate, MRR, Precision@K

#HIT :
def _chunk_is_relevant(chunk: dict, eval_item: dict) -> bool:
    source_match = chunk["source_label"] == eval_item["relevant_source"]
    
    if not source_match:
        return False
    
    keywords = eval_item.get("relevant_chunk_keywords",[])
    if not keywords:
        return True 
    chunk_text_lower = chunk["text"].lower()
    return all(kw.lower() in chunk_text_lower for kw in keywords)

def evaluate_retrieval(eval_item:dict,top_k=5)-> dict:
    
    question=eval_item["question"]
    source = eval_item.get("relevant_source")
    chunks = retrieve_chunks(question,top_k=top_k,source_label=source ,min_similarity=0.0)
    
    hit=False
    first_relevant_rank=None
    relevant_count=0

    for i , chunk in enumerate(chunks):
        if _chunk_is_relevant(chunk=chunk,eval_item=eval_item):
            relevant_count+=1 #Precision@k
            if not hit:
                hit = True
                first_relevant_rank=i+1 #MNN

    mrr=(1/first_relevant_rank) if first_relevant_rank else 0
    precision_at_k=(relevant_count/len(chunks)) if chunks else 0

    return {
        "eval_id": eval_item["id"],
        "metric": "retrieval",
        "passed": hit,
        "hit_rate": int(hit),
        "mrr": round(mrr, 3),
        "precision_at_k": round(precision_at_k, 3),
        "first_relevant_rank": first_relevant_rank,
        "total_chunks_retrieved": len(chunks)
    }

# Stage 2 — Faithfulness
def evaluate_faithfulness(
        question: str,
        answer: str,
        context_chunks:list[str]
)-> dict :
    
    refusal_phrases = [
        "don't have enough information",
        "not mentioned", "not provided",
        "cannot find", "no information", "i don't have"
    ]
    if any(phrase in answer.lower() for phrase in refusal_phrases):
        return {
            "metric": "faithfulness",
            "score": 1.0,
            "passed": True,
            "verdict": "FAITHFUL",
            "reason": "Answer correctly refused — no claims to evaluate"
        }
    
    if not context_chunks:
        return{
            "metric":"faithfulness",
            "score":0.0,
            "passed": False,
            "reason":"No context chunk provided"
        }
    
    context_text="\n\n".join(context_chunks)

    judge_prompt = f"""You are evaluating whether an AI answer is faithful to its source context.

CONTEXT (the only information the AI had access to):
{context_text}

ANSWER (what the AI said):
{answer}

EVALUATION RULES — read carefully:
1. Source citations like [Source 1], [Source 2: Company JD] are formatting labels, 
   NOT factual claims. Never flag these as unsupported.
2. Refusal phrases like "I don't have enough information to answer that" are correct 
   system behavior, NOT factual claims. Never flag these as unsupported.
3. Negative statements ("X is not required", "X is not mentioned") are FAITHFUL 
   if X genuinely does not appear in the context.
4. Only flag a claim as unsupported if the answer states a specific fact 
   that cannot be found anywhere in the provided context.

TASK:
1. Identify every actual factual claim in the answer (ignore citations and refusals)
2. Check each factual claim against the context
3. Flag only claims where specific facts were added beyond what the context contains

Reply in this exact format:
FAITHFULNESS_SCORE: [0.0 to 1.0]
UNSUPPORTED_CLAIMS: [specific unsupported factual claims only, or "None"]
VERDICT: [FAITHFUL or UNFAITHFUL]
REASON: [one sentence]"""
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0,
            messages=[{"role": "user", "content": judge_prompt}]
        )
        judge_text = response.choices[0].message.content.strip()

        score_match = re.search(r"FAITHFULNESS_SCORE:\s*([\d.]+)", judge_text)
        verdict_match = re.search(r"VERDICT:\s*(FAITHFUL|UNFAITHFUL)", judge_text)
        reason_match = re.search(r"REASON:\s*(.+)", judge_text)
        claims_match = re.search(r"UNSUPPORTED_CLAIMS:\s*(.+)", judge_text)
        
        score = float(score_match.group(1)) if score_match else 0.5
        verdict = verdict_match.group(1) if verdict_match else "UNKNOWN"
        reason = reason_match.group(1) if reason_match else ""
        unsupported = claims_match.group(1) if claims_match else ""

        return {
            "metric": "faithfulness",
            "score": round(score, 2),
            "passed": verdict == "FAITHFUL",
            "verdict": verdict,
            "unsupported_claims": unsupported,
            "reason": reason
        }
    
    except Exception as e:
        logger.error(f"Faithfulness Evaluation failed: {e}")
        return {
            "metric": "faithfulness",
            "score": 0.0,
            "passed": False,
            "reason": f"Evaluation error: {e}"
        }
    

#  Stage 3 — Answer Quality

def evaluate_answer_quality(eval_item: dict, answer: str) -> dict:
    if eval_item.get("expected_to_be_unanswerable"):
        grounding_phrases=[
            "don't have enough information",
            "not mentioned",
            "not provided",
            "cannot find",
            "no information",
            "not in the",
            "i don't have"
        ]
        correctly_refused=any(phrase in answer.lower() for phrase in grounding_phrases)

        return {
            "eval_id": eval_item["id"],
            "metric": "grounding",
            "passed": correctly_refused,
            "correctly_refused": correctly_refused,
            "answer_preview": answer[:150]
        }
    

    expected=eval_item.get("expected_answer_contains",[])
    if not expected:
        return {
            "eval_id": eval_item["id"],
            "metric": "answer_quality",
            "passed": True,
            "method": "keyword_match",
            "answer_preview": answer[:150]
        }
    keyword_match = any(kw.lower() in answer.lower() for kw in expected)
    if keyword_match:
        return {
            "eval_id": eval_item["id"],
            "metric": "answer_quality",
            "passed": True,
            "method": "keyword_match",
            "answer_preview": answer[:150]
        }
    
    judge_prompt=f"""Question:{eval_item["question"]}
Expected answer to contain:{expected}
Actual answer: {answer}
Does the answer orrectly address the question?
Reply:PASS or FAIL , then one sentence why."""
    
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0,
        messages=[{"role": "user", "content": judge_prompt}]
    )
    judge_text = response.choices[0].message.content.strip()
    passed = judge_text.upper().startswith("PASS")

    return {
        "eval_id": eval_item["id"],
        "metric": "answer_quality",
        "passed": passed,
        "method": "llm_judge",
        "judge_response": judge_text[:200],
        "answer_preview": answer[:150]
    }


# Entire pipeline

def evaluate_single(eval_item: dict) -> dict:

    result = rag_query(
        eval_item["question"],
        source_label=eval_item.get("relevant_source"),
        min_similarity=0.0,
        use_reranking=True
    )
    answer = result["answer"]

    retrieved_chunks = retrieve_chunks(
        eval_item["question"],
        source_label=eval_item.get("relevant_source"),
        top_k=5,
        min_similarity=0.0
    )
    context_texts = [c["text"] for c in retrieved_chunks]

    retrieval_score = evaluate_retrieval(eval_item)
    answer_score = evaluate_answer_quality(eval_item, answer)
    faithfulness_score = evaluate_faithfulness(
        eval_item["question"], answer, context_texts
    )

    overall=(
        retrieval_score["passed"] and
        answer_score["passed"] and
        faithfulness_score["passed"]
    )

    return {
        "eval_id": eval_item["id"],
        "category": eval_item["category"],
        "question": eval_item["question"],
        "answer": answer,
        "retrieval": retrieval_score,
        "answer_quality": answer_score,
        "faithfulness": faithfulness_score,
        "overall_pass": overall
    }



    


