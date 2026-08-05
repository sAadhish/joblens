import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.career_service import CareerService
from evaluation.joblens_langchain.eval_dataset import EVAL_DATASET
from config import Config
import json
from datetime import datetime

service = CareerService()

def run_langchain_eval():
    print("=" * 55)
    print("LANGCHAIN RAG EVALUATION")
    print(f"Dataset: {len(EVAL_DATASET)} questions")
    print("=" * 55)

    results = []
    passed = 0

    for item in EVAL_DATASET:
        question = item["question"]
        source = item.get("relevant_source")

        result = service.rag.query(question=question, source_label=source)
        answer = result.answer

        # Answer quality check
        if item.get("expected_to_be_unanswerable"):
            refusal_phrases = ["don't have enough information", "not mentioned",
                               "not provided", "cannot find", "no information", "i don't have"]
            ans_pass = any(p in answer.lower() for p in refusal_phrases)
        else:
            expected = item.get("expected_answer_contains", [])
            ans_pass = any(kw.lower() in answer.lower() for kw in expected) if expected else True

        passed += int(ans_pass)

        print(f"[{item['id']}] {'✅' if ans_pass else '❌'} {question[:55]}...")
        if not ans_pass:
            print(f"  Expected: {item.get('expected_answer_contains')}")
            print(f"  Got: {answer[:100]}")

        results.append({
            "eval_id": item["id"],
            "category": item["category"],
            "passed": ans_pass,
            "answer": answer
        })

    total = len(EVAL_DATASET)
    score = round(passed / total, 3)

    print()
    print("=" * 55)
    print("RESULTS")
    print("=" * 55)
    print(f"LangChain RAG Score : {score*100:.0f}%  ({passed}/{total})")
    print(f"Hand-built RAG Score: 85%  (11/13)")
    print(f"Difference          : {(score - 0.85)*100:+.0f}%")

    by_cat = {}
    for r in results:
        cat = next(i["category"] for i in EVAL_DATASET if i["id"] == r["eval_id"])
        by_cat.setdefault(cat, {"total": 0, "passed": 0})
        by_cat[cat]["total"] += 1
        by_cat[cat]["passed"] += int(r["passed"])

    print("\nBy Category:")
    for cat, v in by_cat.items():
        print(f"  {cat:<25}: {round(v['passed']/v['total']*100)}%")

    os.makedirs("eval_results", exist_ok=True)
    fname = f"eval_results/langchain_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(fname, "w") as f:
        json.dump({"score": score, "results": results}, f, indent=2)
    print(f"\nSaved: {fname}")

if __name__ == "__main__":
    run_langchain_eval()