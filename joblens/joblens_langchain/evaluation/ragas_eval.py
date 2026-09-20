# ===================================
# RAGAS EVALUATION
# Standardized RAG evaluation framework
# Run this after any pipeline change to get comparable scores
# ===================================

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from datasets import Dataset
from services.career_service import CareerService
from config import Config
from logger import logger
import json
from datetime import datetime


# -------------------------------------------------------
# SETUP — tell RAGAS which LLM and embeddings to use
# -------------------------------------------------------

# RAGAS needs an LLM to act as judge for most metrics
ragas_llm = LangchainLLMWrapper(
    ChatGroq(
        api_key=Config.GROQ_API_KEY,
        model=Config.LLM_MODEL,
        temperature=0
    )
)

# RAGAS needs embeddings for answer_relevancy metric
ragas_embeddings = LangchainEmbeddingsWrapper(
    HuggingFaceEmbeddings(model_name=Config.EMBEDDING_MODEL)
)


# -------------------------------------------------------
# EVAL DATASET
# RAGAS needs: question, answer, contexts, ground_truth
# ground_truth is optional but improves context_recall accuracy
# -------------------------------------------------------

RAGAS_DATASET = [
    {
        "question": "What Python frameworks does the Sarvam AI role require?",
        "ground_truth": "FastAPI",
        "source_label": "Sarvam AI JD"
    },
    {
        "question": "How many years of experience does the Sarvam AI role need?",
        "ground_truth": "3 to 6 years",
        "source_label": "Sarvam AI JD"
    },
    {
        "question": "What database tools does the Razorpay Data Engineer role require?",
        "ground_truth": "SQL, Snowflake, dbt",
        "source_label": "Razorpay JD"
    },
    {
        "question": "Does the Haptik role require RAG experience?",
        "ground_truth": "RAG experience is listed as a strong plus, not a hard requirement",
        "source_label": "Haptik JD"
    },
    {
        "question": "What BI tools has the candidate used?",
        "ground_truth": "Qlik Sense, Power BI, Tableau",
        "source_label": "My Resume"
    },
    {
        "question": "What cloud platforms has the candidate worked with?",
        "ground_truth": "AWS including EC2, S3, RDS, CloudWatch",
        "source_label": "My Resume"
    },
]


def build_ragas_dataset(service: CareerService) -> Dataset:
    """
    Runs each question through the RAG pipeline and
    collects: question, answer, contexts, ground_truth.

    This is what RAGAS needs to compute all four metrics.
    """

    questions = []
    answers = []
    contexts = []
    ground_truths = []

    print("Building RAGAS dataset...")
    for item in RAGAS_DATASET:
        question = item["question"]
        source = item["source_label"]

        # Get the RAG answer
        result = service.rag.query(question=question, source_label=source)

        # Get the retrieved chunks (contexts)
        chunks = service.vector.retrieve(
            question=question,
            source_label=source,
            top_k=3
        )
        chunk_texts = [c.text for c in chunks]

        questions.append(question)
        answers.append(result.answer)
        contexts.append(chunk_texts)
        ground_truths.append(item["ground_truth"])

        print(f"  ✓ {question[:55]}...")

    return Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    })


def run_ragas_evaluation():
    print("=" * 55)
    print("RAGAS EVALUATION — JobLens LangChain RAG")
    print("=" * 55)

    service = CareerService()
    dataset = build_ragas_dataset(service)

    print("\nRunning RAGAS metrics...")
    print("(Each metric makes LLM calls — this takes ~30-60 seconds)")

    results = evaluate(
        dataset=dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        ],
        llm=ragas_llm,
        embeddings=ragas_embeddings,
    )

    # Print results
    print()
    print("=" * 55)
    print("RAGAS SCORES")
    print("=" * 55)

    scores = results.to_pandas()
    means = scores[["faithfulness", "answer_relevancy",
                     "context_precision", "context_recall"]].mean()

    print(f"Faithfulness      : {means['faithfulness']:.3f}")
    print(f"Answer Relevancy  : {means['answer_relevancy']:.3f}")
    print(f"Context Precision : {means['context_precision']:.3f}")
    print(f"Context Recall    : {means['context_recall']:.3f}")
    print(f"\nOverall (mean)    : {means.mean():.3f}")

    # Per-question breakdown
    print()
    print("Per Question:")
    for i, row in scores.iterrows():
        print(f"\n  Q: {RAGAS_DATASET[i]['question'][:55]}...")
        print(f"     Faithfulness: {row['faithfulness']:.2f} | "
              f"Relevancy: {row['answer_relevancy']:.2f} | "
              f"Precision: {row['context_precision']:.2f} | "
              f"Recall: {row['context_recall']:.2f}")

    # Compare with hand-built evaluator
    print()
    print("=" * 55)
    print("COMPARISON")
    print("=" * 55)
    print(f"Hand-built evaluator overall : 85%")
    print(f"RAGAS overall (this run)     : {means.mean()*100:.0f}%")
    print()
    print("Note: These measure slightly different things.")
    print("Hand-built: binary pass/fail per question")
    print("RAGAS: continuous 0-1 scores per metric")

    # Save results
    os.makedirs("eval_results", exist_ok=True)
    fname = f"eval_results/ragas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(fname, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "scores": means.to_dict(),
            "overall": float(means.mean())
        }, f, indent=2)
    print(f"\nSaved: {fname}")

    return results


if __name__ == "__main__":
    run_ragas_evaluation()