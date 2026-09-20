# debug_resume.py
import sys, os
sys.path.append(os.path.abspath("."))

from services.career_service import CareerService

service = CareerService()

questions = [
    "What BI tools has the candidate used?",
    "What cloud platforms has the candidate worked with?",
    "How many Qlik Sense applications has the candidate built?",
]

for q in questions:
    chunks = service.vector.retrieve(
        question=q,
        source_label="My Resume",
        top_k=3
    )
    print(f"\nQ: {q}")
    print(f"Chunks found: {len(chunks)}")
    for c in chunks:
        print(f"  score={c.score} | {c.text[:80]}")