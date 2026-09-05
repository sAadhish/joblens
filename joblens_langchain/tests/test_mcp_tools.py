import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server.tools import (
    search_joblens,
    ask_career_question,
    list_indexed_companies,
    analyze_skill_gap
)

print("=" * 55)
print("TEST 1 — list_indexed_companies")
print("=" * 55)
result = list_indexed_companies()
print(result)

print()
print("=" * 55)
print("TEST 2 — search_joblens")
print("=" * 55)
result = search_joblens("Python backend requirements", "Sarvam AI")
print(result[:300])

print()
print("=" * 55)
print("TEST 3 — ask_career_question")
print("=" * 55)
result = ask_career_question("What does the Haptik AI Engineer role require?", "Haptik")
print(result[:300])

print()
print("=" * 55)
print("TEST 4 — analyze_skill_gap")
print("=" * 55)
result = analyze_skill_gap(
    "Python, SQL, Power BI, Tableau, FastAPI, Snowflake, AWS",
    "Freshworks"
)
print(result)