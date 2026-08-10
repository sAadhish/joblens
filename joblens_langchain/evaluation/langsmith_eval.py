import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langsmith import Client
from langsmith.evaluation import evaluate as ls_evaluate
from services.career_service import CareerService
from config import Config
from langsmith_setup import setup_langsmith
from logger import logger

setup_langsmith()
client = Client()
service = CareerService()


# -------------------------------------------------------
# DATASET 
# -------------------------------------------------------

DATASET_NAME = "JobLens RAG Eval v1"

EVAL_EXAMPLES = [
    {
        "inputs": {
            "question": "What Python frameworks does the Sarvam AI role require?",
            "source_label": "Sarvam AI JD"
        },
        "outputs": {
            "expected": "FastAPI"
        }
    },
    {
        "inputs": {
            "question": "How many years of experience does the Sarvam AI role need?",
            "source_label": "Sarvam AI JD"
        },
        "outputs": {
            "expected": "3 to 6 years"
        }
    },
    {
        "inputs": {
            "question": "Does the Haptik role require RAG experience?",
            "source_label": "Haptik JD"
        },
        "outputs": {
            "expected": "RAG is a strong plus, not a hard requirement"
        }
    },
    {
        "inputs": {
            "question": "What BI tools has the candidate used?",
            "source_label": "My Resume"
        },
        "outputs": {
            "expected": "Qlik Sense, Power BI, Tableau"
        }
    },
    {
        "inputs": {
            "question": "What is the salary for the Sarvam AI role?",
            "source_label": "Sarvam AI JD"
        },
        "outputs": {
            "expected": "not mentioned"
        }
    },
]


#create dataset in langchain
def create_or_get_dataset()->str:
    existing = [d.name for d in client.list_datasets()]

    if DATASET_NAME in existing:
        logger.info(f"Dataset already exists: {DATASET_NAME}")
        return DATASET_NAME

    dataset=client.create_dataset(
        dataset_name=DATASET_NAME,
        description="JobLens RAG evaluation dataset — factual, grounding, resume questions"
    ) 

    client.create_example(
        inputs=[e["inputs"] for e in EVAL_EXAMPLES],
        outputs=[e["outputs"] for e in EVAL_EXAMPLES],
        dataset_id=dataset.id
    )

    logger.info(f"Created dataset: {DATASET_NAME} with {len(EVAL_EXAMPLES)} examples")
    return DATASET_NAME


# call rag
def rag_target(inputs:dict)->dict:
    result = service.rag.query(
        question=inputs["question"],
        source_label=inputs.get("source_label")
    )
    return {"answer": result.answer}


#score evaluator 
def contains_expected(run,example):
    answer = run.outputs.get("answer", "").lower()
    expected = example.outputs.get("expected", "").lower()

    if "not mentioned" in expected:
        refusal_phrases = [
            "don't have enough information",
            "not mentioned", "not provided"
        ]

        score =1 if any(p in answer for p in refusal_phrases) else 0
    else :
        keywords = [kw.strip().lower() for kw in expected.split(",")]
        score = 1 if any(kw in answer for kw in keywords) else 0

    return {
        "key": "contains_expected",
        "score": score,
        "comment": f"Expected: {expected[:50]} | Got: {answer[:50]}"
    }

#check if its hallucinated
def is_grounded(run, example) -> dict:
  
    answer = run.outputs.get("answer", "").lower()
    expected = example.outputs.get("expected", "").lower()

    if "not mentioned" in expected:
        hallucinated = not any(p in answer for p in [
            "don't have", "not mentioned", "not provided", "no information"
        ])
        return {
            "key": "grounded",
            "score": 0 if hallucinated else 1,
            "comment": "Hallucination detected" if hallucinated else "Correctly refused"
        }

    return {
        "key": "grounded",
        "score": 1, 
        "comment": "N/A for this question type"}

def run_langsmith_evaluation():
    print("=" * 55)
    print("LANGSMITH EVALUATION")
    print("=" * 55)

    dataset_name=create_or_get_dataset()

    print(f"\nRunning evaluation on dataset: {dataset_name}")
    print("Results will appear at smith.langchain.com\n")

    results=ls_evaluate(
        rag_target,
        data=dataset_name,
        evaluators=[contains_expected, is_grounded],
        metadata={
            "version": "langchain-oop",
            "embedding_model": Config.EMBEDDING_MODEL,
            "llm_model": Config.LLM_MODEL,
        }
    )
    print("\nEvaluation complete.")
    print("Open smith.langchain.com → Projects → joblens → Experiments")
    print("to see full traces, scores, and per-question breakdown.")

    return results


if __name__ == "__main__":
    run_langsmith_evaluation()



