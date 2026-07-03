import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from career_qa import ask_about_match, compare_my_top_matches

candidate_profile = """
1 year experience as BI Developer and Data Analyst.
Skills: Qlik Sense, Power BI, Tableau, SQL, Python, 
Snowflake, AWS, Apache Airflow, Databricks, FastAPI.
"""

print("=" * 55)
print("TEST 1 — Ask about your #1 best match, automatically")
print("=" * 55)

result = ask_about_match(
    candidate_profile,
    "What skills does this role require that I should focus on learning?",
    match_rank=1
)
print(f"\nMatched: {result.get('matched_company')} (score: {result.get('match_score')})")
print(f"A: {result['answer']}")


print()
print("=" * 55)
print("TEST 2 — Compare top 2 matches automatically")
print("=" * 55)

result2 = compare_my_top_matches(
    candidate_profile,
    "Which role is the better fit for me right now?",
    top_n=2
)
print(f"A: {result2['answers']}")