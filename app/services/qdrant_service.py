import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from dotenv import load_dotenv

load_dotenv()

client = QdrantClient(
    url = os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

COLLECTION_NAME = "pyq_Collection"

def create_collection():
    client.recreate_collection(
        collection_name = COLLECTION_NAME,
        vectors_config=VectorParams(
            size=384,
            distance = Distance.COSINE
        ),
    )
    
def insert_vector(question_id, vector , payload):
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=question_id,
                vector=vector,
                payload=payload,
            )
        ]
    )
    

def search_vector(query_vector , limit=5):
    return client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=limit
    )