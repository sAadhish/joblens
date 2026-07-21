from loader.loader import DocumentLoader

loader = DocumentLoader()

docs = loader.load("data/gen ai resume.pdf")

print(f"Pages loaded: {len(docs)}")

print("-" * 50)

print(docs[0].page_content[:500])

print("-" * 50)

print(docs[0].metadata)