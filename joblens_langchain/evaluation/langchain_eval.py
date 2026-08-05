import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.career_service import CareerService
from evaluation.joblens_langchain.eval_dataset import EVAL_DATASET


def run_langchain_eval():
    print("=" * 55)
    print("LANGCHAIN RAG EVALUATION")
    print("=" * 55)

    service = CareerService()
    results = []
    passed = 0

    for item in EVAL_DATASET:
        question = item["question"]
        source = item.get("relevant_source")

        result = service.rag.query(question=question, source_label=source)
        answer = result.answer

        if item.get("expected_to_be_unanswerable"):
            refusal_phrases = [
                "don't have enough information",
                "not mentioned",
                "not provided",
                "no information",
                "i don't have"
            ]
            ans_pass = any(p in answer.lower() for p in refusal_phrases)
        else:
            expected = item.get("expected_answer_contains", [])
            if expected:
                ans_pass = any(kw.lower() in answer.lower() for kw in expected)
            else:
                ans_pass = True

        passed += int(ans_pass)
        status = "PASS" if ans_pass else "FAIL"
        print(f"[{item['id']}] {status} | {question[:50]}...")

        if not ans_pass:
            print(f"  Expected : {item.get('expected_answer_contains')}")
            print(f"  Got      : {answer[:100]}")

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
    print("FINAL RESULTS")
    print("=" * 55)
    print(f"LangChain RAG : {score*100:.0f}%  ({passed}/{total})")
    print(f"Hand-built RAG: 85%  (11/13)")
    print(f"Difference    : {(score - 0.85)*100:+.0f}%")

    by_cat = {}
    for r in results:
        cat = next(
            i["category"] for i in EVAL_DATASET
            if i["id"] == r["eval_id"]
        )
        by_cat.setdefault(cat, {"total": 0, "passed": 0})
        by_cat[cat]["total"] += 1
        by_cat[cat]["passed"] += int(r["passed"])

    print("\nBy Category:")
    for cat, v in by_cat.items():
        pct = round(v["passed"] / v["total"] * 100)
        print(f"  {cat:<25}: {pct}%")

    os.makedirs("eval_results", exist_ok=True)
    fname = f"eval_results/langchain_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(fname, "w") as f:
        json.dump({"score": score, "results": results}, f, indent=2)
    print(f"\nSaved: {fname}")


if __name__ == "__main__":
    run_langchain_eval()