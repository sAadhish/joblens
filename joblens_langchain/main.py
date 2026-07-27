from loader.loader import DocumentLoader
from chunking.chunker import TextChunker
from services.injection import IngestionService
from vectorstore.qdrant_service import QdrantService


loader = DocumentLoader()
chunker = TextChunker()

# Load the document
documents = loader.load("data/gen ai resume.pdf")

# Chunk the document
chunks = chunker.chunk(
    documents=documents,
    source_label="Resume"
)

print("=" * 70)
print(f"Total Chunks : {len(chunks)}")
print("=" * 70)

for chunk in chunks:
    print(f"\nChunk Index : {chunk.chunk_index}")
    print(f"Source      : {chunk.source_label}")
    print(f"Characters  : {chunk.char_count}")
    print(f"Strategy    : {chunk.strategy}")
    print("-" * 70)
    print(chunk.text[:300])   # first 300 characters





def main():

    ingestion = IngestionService()
    qdrant = QdrantService()

    chunks = ingestion.ingest(
        source="data/gen ai resume.pdf",
        source_label="My Resume"
    )

    result = qdrant.index_chunks(chunks)

    print(result)


if __name__ == "__main__":
    main()