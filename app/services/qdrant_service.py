import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from dotenv import load_dotenv

load_dotenv()

client = QdrantClient(
    url = os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    timeout=60
)

COLLECTION_NAME = "pyq_Collection"

def create_collection():
    collections = client.get_collections().collections
    collection_names = [c.name for c in collections]

    if COLLECTION_NAME in collection_names:
        collection_info = client.get_collection(collection_name=COLLECTION_NAME)
        # Check if the vector size is 1024
        if collection_info.config.params.vectors.size != 3072:
            print(f"Dimension mismatch in {COLLECTION_NAME}. Deleting and recreating...")
            client.delete_collection(collection_name=COLLECTION_NAME)
            collection_names.remove(COLLECTION_NAME)

    if COLLECTION_NAME not in collection_names:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=3072,
                distance=Distance.COSINE
            ),
        )
    
def insert_vector(question_id, vector, payload):
    # Ensure collection exists before every insert (safety guard)
    create_collection()
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
    

def search_vector(query_vector, limit=5, offset=0):
    create_collection()  # ensure collection exists
    response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit,
        offset=offset
    )

    # return (id, score) tuples
    return [(point.id, point.score) for point in response.points]

