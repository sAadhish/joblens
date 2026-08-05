# check_qdrant.py
from services.career_service import CareerService
service = CareerService()
print(service.collection_stats())

# Check if any resume chunks exist
from vectorstore.qdrant_service import QdrantService
qs = QdrantService()
chunks = qs.retrieve("BI tools Qlik Sense", source_label="My Resume", top_k=3)
print(f"Resume chunks found: {len(chunks)}")



"""
from services.career_service import CareerService
s = CareerService()
print('Total vectors:', s.collection_stats())

# Check if resume exists
from qdrant_client import QdrantClient
from config import Config
client = QdrantClient(url=Config.QDRANT_URL, api_key=Config.QDRANT_API_KEY)
results = client.scroll(collection_name=Config.QDRANT_COLLECTION, limit=20, with_payload=True)
labels = set(p.payload.get('metadata', {}).get('source_label', 'unknown') for p in results[0])
print('Sources in Qdrant:', labels)
"""