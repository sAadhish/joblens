from rag import retrieve_multi_source

results = retrieve_multi_source(
    "Which role is the better fit for me right now?",
    source_label=["Razorpay JD", "My Resume"],
    per_source_k=2,
    min_similarity=0.05   # deliberately very low, just to see if anything's there at all
)

for label, chunks in results.items():
    print(f"{label}: {len(chunks)} chunks")
    for c in chunks:
        print(f"  score={c['score']} | {c['text'][:80]}")