# clean_qdrant.py
import sys; sys.path.append('.')
from qdrant_client import QdrantClient
from config import Config

client = QdrantClient(url=Config.QDRANT_URL, api_key=Config.QDRANT_API_KEY)
client.delete_collection(Config.QDRANT_COLLECTION)
print("Collection deleted")