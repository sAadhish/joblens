# ===================================
# EVAL REPORT — With Regression Detection
# ===================================

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import glob
from datetime import datetime
from joblens_langchain.evaluation.joblens_langchain.eval_dataset import EVAL_DATASET
from joblens_langchain.evaluation.joblens_langchain.evaluator import evaluate_single


def run_evaluation(dataset: list = EVAL_DATASET) -> dict:

    print("=" * 55)
    print("JOBLENS RAG EVALUATION — PRODUCTION GRADE")
    print(f"Dataset: {len(dataset)} questions")
    print("=" * 55)

    results = []
    counters = {
        "hit": 0, "mrr_total": 0.0,
        "precision_total": 0.0,
        "answer_passed": 0,
        "faithfulness_passed": 0,
        "overall_passed": 0
    }

    category_results = {}

    for item in dataset:
        print(f"\n[{item['id']}] ({item['category']}) {item['question'][:55]}...")
        result = evaluate_single(item)
        results.append(result)

        ret = result["retrieval"]
        ans = result["answer_quality"]
        faith = result["faithfulness"]

        counters["hit"] += ret["hit_rate"]
        counters["mrr_total"] += ret["mrr"]
        counters["precision_total"] += ret["precision_at_k"]
        counters["answer_passed"] += int(ans["passed"])
        counters["faithfulness_passed"] += int(faith["passed"])
        counters["overall_passed"] += int(result["overall_pass"])

        # Track by category
        cat = item["category"]
        if cat not in category_results:
            category_results[cat] = {"total": 0, "passed": 0}
        category_results[cat]["total"] += 1
        category_results[cat]["passed"] += int(result["overall_pass"])

        print(f"  Retrieval  : hit={'✅' if ret['hit_rate'] else '❌'} | "
              f"MRR={ret['mrr']} | P@K={ret['precision_at_k']}")
        print(f"  Answer     : {'✅' if ans['passed'] else '❌'}")
        print(f"  Faithfulness: {'✅' if faith['passed'] else '❌'} "
              f"(score={faith['score']})")

    total = len(dataset)
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_questions": total,
        "scores": {
            "hit_rate": round(counters["hit"] / total, 3),
            "mrr": round(counters["mrr_total"] / total, 3),
            "precision_at_k": round(counters["precision_total"] / total, 3),
            "answer_quality": round(counters["answer_passed"] / total, 3),
            "faithfulness": round(counters["faithfulness_passed"] / total, 3),
            "overall": round(counters["overall_passed"] / total, 3),
        },
        "by_category": {
            cat: round(v["passed"] / v["total"], 2) for cat, v in category_results.items()
        },
        "results": results
    }

    # Save with timestamp
    os.makedirs("eval_results", exist_ok=True)
    filename = f"eval_results/eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(summary, f, indent=2)

    # Print final scores
    print()
    print("=" * 55)
    print("FINAL SCORES")
    print("=" * 55)
    s = summary["scores"]
    print(f"Hit Rate       : {s['hit_rate']*100:.0f}%")
    print(f"MRR            : {s['mrr']:.3f}")
    print(f"Precision@K    : {s['precision_at_k']*100:.0f}%")
    print(f"Answer Quality : {s['answer_quality']*100:.0f}%")
    print(f"Faithfulness   : {s['faithfulness']*100:.0f}%")
    print(f"Overall        : {s['overall']*100:.0f}%")
    print()
    print("By Category:")
    for cat, score in summary["by_category"].items():
        print(f"  {cat:<25} : {score*100:.0f}%")

    # Regression check
    _check_regression(filename, results)

    print(f"\nSaved: {filename}")
    return summary


def _check_regression(current_file: str, current_results: list):


    all_files = sorted(glob.glob("eval_results/eval_*.json"))
    if len(all_files) < 2:
        print("\n(No previous run to compare against — baseline established)")
        return

    # Load the previous run (second-to-last file)
    prev_file = all_files[-2]
    with open(prev_file) as f:
        prev_data = json.load(f)

    prev_by_id = {r["eval_id"]: r for r in prev_data["results"]}
    curr_by_id = {r["eval_id"]: r for r in current_results}

    regressions = []
    improvements = []

    for eval_id, curr in curr_by_id.items():
        if eval_id not in prev_by_id:
            continue
        prev = prev_by_id[eval_id]
        was_passing = prev["overall_pass"]
        now_passing = curr["overall_pass"]

        if was_passing and not now_passing:
            regressions.append(eval_id)
        elif not was_passing and now_passing:
            improvements.append(eval_id)

    print()
    print("=" * 55)
    print("REGRESSION REPORT")
    print("=" * 55)
    if regressions:
        print(f"⚠️  REGRESSIONS ({len(regressions)}) — these PASSED before, FAIL now:")
        for r in regressions:
            print(f"   → {r}: {curr_by_id[r]['question'][:60]}")
    else:
        print("✅ No regressions — nothing that was passing is now failing")

    if improvements:
        print(f"\n✅ IMPROVEMENTS ({len(improvements)}) — these FAILED before, PASS now:")
        for i in improvements:
            print(f"   → {i}: {curr_by_id[i]['question'][:60]}")


if __name__ == "__main__":
    run_evaluation()