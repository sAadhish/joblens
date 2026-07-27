from loader.loader import DocumentLoader
from chunking.chunker import TextChunker


class IngestionService:

    def __init__(self):
        self.loader = DocumentLoader()
        self.chunker = TextChunker()

    def ingest(self, source: str, source_label: str):
        print("Loading document...")
        documents = self.loader.load(source)
        print(f"Loaded {len(documents)} document(s)")

        print("Splitting document...")
        chunks = self.chunker.chunk(documents, source_label)

        return chunks

    def ingest_text(self, text: str, source_label: str):
        print("Loading document...")
        documents = self.loader.load_from_string(text, source_label)
        print(f"Loaded {len(documents)} document(s)")

        print("Splitting document...")
        chunks = self.chunker.chunk(documents, source_label)

        return chunks