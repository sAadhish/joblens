from config import collection,rag_collection
print(f"Total documents in Stage 1 collection: {collection.count()}")
print(f"Total documents in Stage 2 collection: {rag_collection.count()}")

from config import rag_collection
results = rag_collection.get(where={"source_label": "My Resume"})
print(len(results["ids"]))
