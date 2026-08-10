import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ragas import EvaluationDataset, SingleTurnSample, evaluate
from ragas.metrics import Faithfulness, AnswerRelevancy, ContextPrecision, ContextRecall
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from services.career_service import CareerService
from config import Config
from logger import logger
import json
from datetime import datetime

#setup judges

evaluator_llm =LangchainLLMWrapper(
    ChatGroq(
        api_key=Config.GROQ_API_KEY,
        model=Config.LLM_MODEL,
        temperature=0
    )
)

evaluator_embeddings = LangchainEmbeddingsWrapper(
    HuggingFaceEmbeddings(
        model_name=Config.EMBEDDING_MODEL
    )
)

metrics=[
    Faithfulness(llm=evaluator_llm),
    AnswerRelevancy(llm=evaluator_llm,embeddings=evaluator_embeddings),
    ContextPrecision(llm=evaluator_llm),
    ContextRecall(llm=evaluator_llm),
]

#eval data set

RAGAS_DATASET = [
    {
        "user_input": "What Python frameworks does the Sarvam AI role require?",
        "reference": "FastAPI",
        "source_label": "Sarvam AI JD"
    },
    {
        "user_input": "How many years of experience does the Sarvam AI role need?",
        "reference": "3 to 6 years",
        "source_label": "Sarvam AI JD"
    },
    {
        "user_input": "What database tools does the Razorpay Data Engineer role require?",
        "reference": "SQL, Snowflake, dbt",
        "source_label": "Razorpay JD"
    },
    {
        "user_input": "Does the Haptik role require RAG experience?",
        "reference": "RAG experience is a strong plus, not a hard requirement",
        "source_label": "Haptik JD"
    },
    {
        "user_input": "What BI tools has the candidate used?",
        "reference": "Qlik Sense, Power BI, Tableau",
        "source_label": "My Resume"
    },
    {
        "user_input": "What cloud platforms has the candidate worked with?",
        "reference": "AWS including EC2, S3, RDS, CloudWatch",
        "source_label": "My Resume"
    },
]


def build_ragas_dataset(service: CareerService) -> EvaluationDataset:
  
    samples = []

    print("Building RAGAS dataset...")
    for item in RAGAS_DATASET:
        question = item["user_input"]
        source = item["source_label"]

        # Get RAG answer
        result = service.rag.query(question=question, source_label=source)

        # Get retrieved chunks
        chunks = service.vector.retrieve(
            question=question,
            source_label=source,
            top_k=3
        )
        chunk_texts = [c.text for c in chunks]

        sample=SingleTurnSample(
            user_input=question,
            response=result.answer,
            retrieved_contexts=chunk_texts,
            reference=item["reference"]
        )

        samples.append(sample)
        print(f"  ✓ {question[:55]}...")
    return EvaluationDataset(samples=samples)

def run_ragas_evaluation():
    print("=" * 55)
    print("RAGAS EVALUATION v0.4 — JobLens LangChain RAG")
    print("=" * 55)

    service = CareerService()
    dataset = build_ragas_dataset(service)

    print("\nRunning RAGAS metrics...")
    print("(Makes multiple LLM calls — takes ~60-120 seconds)")

    results = evaluate(
        dataset=dataset,
        metrics=metrics,
    )

    # Print scores
    df = results.to_pandas()
    metric_cols = ["faithfulness", "answer_relevancy",
                   "context_precision", "context_recall"]

    print()
    print("=" * 55)
    print("RAGAS SCORES")
    print("=" * 55)
    means = df[metric_cols].mean()
    print(f"Faithfulness      : {means['faithfulness']:.3f}")
    print(f"Answer Relevancy  : {means['answer_relevancy']:.3f}")
    print(f"Context Precision : {means['context_precision']:.3f}")
    print(f"Context Recall    : {means['context_recall']:.3f}")
    print(f"\nOverall (mean)    : {means.mean():.3f}")

    print()
    print("Per Question:")
    for i, row in df.iterrows():
        print(f"\n  Q: {RAGAS_DATASET[i]['user_input'][:55]}...")
        print(f"     Faith={row['faithfulness']:.2f} | "
              f"Relevancy={row['answer_relevancy']:.2f} | "
              f"Precision={row['context_precision']:.2f} | "
              f"Recall={row['context_recall']:.2f}")

    print()
    print("=" * 55)
    print("COMPARISON")
    print("=" * 55)
    print(f"Hand-built evaluator : 85%  (binary pass/fail)")
    print(f"RAGAS overall        : {means.mean()*100:.0f}%  (continuous 0-1)")

    # Save
    os.makedirs("eval_results", exist_ok=True)
    fname = f"eval_results/ragas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(fname, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "ragas_version": "0.4.x",
            "scores": means.to_dict(),
            "overall": float(means.mean())
        }, f, indent=2)
    print(f"\nSaved: {fname}")

    return results


if __name__ == "__main__":
    run_ragas_evaluation()