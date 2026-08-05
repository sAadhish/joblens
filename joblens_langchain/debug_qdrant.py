# debug_qdrant.py
from qdrant_client import QdrantClient
from config import Config

client = QdrantClient(url=Config.QDRANT_URL, api_key=Config.QDRANT_API_KEY)

# Look at the first stored point's actual payload structure
results = client.scroll(
    collection_name=Config.QDRANT_COLLECTION,
    limit=2,
    with_payload=True
)

for point in results[0]:
    print("Payload:", point.payload)