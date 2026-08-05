from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_core.documents import Document
from qdrant_client.models import Distance, VectorParams,Filter, FieldCondition, MatchValue
from qdrant_client.http.models import PayloadSchemaType
from models.schemas import DocumentChunk, RetrievedChunk, IndexingResult
from vectorstore.embedding_service import EmbeddingService
from config import Config
from logger import logger

class QdrantService:

    def __init__(self):

        self.client=QdrantClient(
            url=Config.QDRANT_URL,
            api_key=Config.QDRANT_API_KEY
        )

        self.embeddings = EmbeddingService.get_embedding_model()
        
        self._ensure_collection()

        self._create_payload_indexes()

        self.vectorstore=QdrantVectorStore(
            client=self.client,
            collection_name=Config.QDRANT_COLLECTION,
            embedding=self.embeddings
        )

        logger.info(f"QdrantService initialized using collection '{Config.QDRANT_COLLECTION}'")

    def _ensure_collection(self):
        collections=self.client.get_collections().collections
        existing=[c.name for c in collections]

        if Config.QDRANT_COLLECTION not in existing:

            self.client.create_collection(
                collection_name=Config.QDRANT_COLLECTION,
                vectors_config=VectorParams(
                size=Config.EMBEDDING_DIMENSION,
                distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection: {Config.QDRANT_COLLECTION}")
        else:
            logger.info(f"Using existing collection: {Config.QDRANT_COLLECTION}")

    def _create_payload_indexes(self):

        indexes=[
            "metadata.source_label",
            "metadata.document_type",
            "metadata.user_id",
            "metadata.company_name"
        ]

        for field in indexes:
            try:
                self.client.create_payload_index(
                    collection_name=Config.QDRANT_COLLECTION,
                    field_name=field,
                    field_schema=PayloadSchemaType.KEYWORD
                )
            except Exception:
                logger.info(f"Payload index already exists: {field}")

    def _prepare_documents(
            self,
            chunks: list[DocumentChunk]
    )-> list[Document]:
        
        documents=[]
        for chunk in chunks:
            documents.append(
                Document(
                    page_content=chunk.text,
                    metadata={
                    "source_label": chunk.source_label,
                    "chunk_index": chunk.chunk_index,
                    "char_count": chunk.char_count,               
                    "document_type": getattr(chunk, "document_type", "unknown"),
                    "company_name": getattr(chunk, "company_name", None),
                    "user_id": getattr(chunk, "user_id", None),
                    }
                )
            )

        return documents

    def index_chunks(self,chunks: list[DocumentChunk]) -> IndexingResult:
        if not chunks:
            return IndexingResult(
                source_label="unknown",
                chunks_indexed=0,
                success=False,
                error="No chunks provided"
            )
        source_label = chunks[0].source_label

        try:
            docs=self._prepare_documents(chunks)
            self.vectorstore.add_documents(docs)
            logger.info(f"Indexed {len(chunks)} chunks for '{source_label}'")

            return IndexingResult(
                    source_label=source_label,
                    chunks_indexed=len(chunks),
                    success=True
                   )

        except Exception as e:
            logger.error(f"Indexing failed for '{source_label}': {e}")
            return IndexingResult(
                source_label=source_label,
                chunks_indexed=0,
                success=False,
                error=str(e)
            )



    def retrieve(
            self,
            question : str,
            source_label: str = None,
            top_k: int = Config.RETRIEVAL_TOP_K
    )->list[RetrievedChunk]:

        filter_condition = None 
        if source_label:
            filter_condition=Filter(
                must=[
                    FieldCondition(
                        key="metadata.source_label",
                        match=MatchValue(value=source_label)
                    )
                ]
            ) # the filter must full fill this field condition

        results = self.vectorstore.similarity_search_with_score(
                query=question,
                k=top_k,
                filter=filter_condition
            )

        retrieved =[]
        for doc, score in results:
            retrieved.append(RetrievedChunk(
                    text=doc.page_content,
                    source_label=doc.metadata.get("source_label", "unknown"),
                    score=round(float(score), 3),
                    chunk_index=doc.metadata.get("chunk_index", 0)
                ))

        logger.info(f"Retrieved {len(retrieved)} chunks for query (source: {source_label})")
        return retrieved


    def collection_count(self) -> int:
        return self.client.count(collection_name=Config.QDRANT_COLLECTION).count

# DEBUG

    def debug_payloads(self, limit: int = 10):

        print("\n" + "=" * 70)

        print("DEBUGGING QDRANT PAYLOADS")

        print("=" * 70)

        points, _ = self.client.scroll(

            collection_name=Config.QDRANT_COLLECTION,

            limit=limit,

            with_payload=True,

            with_vectors=False,

        )

        print(f"Found {len(points)} points\n")

        for i, point in enumerate(points, start=1):

            print("-" * 70)

            print(f"Point {i}")

            print("-" * 70)

            print("ID:")

            print(point.id)

            print("\nPayload:")

            print(point.payload)

            print()

        print("=" * 70)




        
        





    

