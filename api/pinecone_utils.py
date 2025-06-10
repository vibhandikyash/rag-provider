from pinecone import Pinecone
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

print('PINECONE_API_KEY:', os.getenv("PINECONE_API_KEY"))
print('PINECONE_ENVIRONMENT:', os.getenv("PINECONE_ENVIRONMENT"))
print('PINECONE_INDEX_NAME:', os.getenv("PINECONE_INDEX_NAME"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

def init_pinecone():
    """Initialize Pinecone client."""
    
    print(pc.list_indexes())


    index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
    index_info = pc.describe_index(os.getenv("PINECONE_INDEX_NAME"))

    print('Index :', index)
    print(f"Index info: {index_info}")

def create_index_if_not_exists():
    """Create Pinecone index if it doesn't exist."""
    index_name = os.getenv("PINECONE_INDEX_NAME")

    print(pc.list_indexes())

    if index_name not in pc.list_indexes():
        raise RuntimeError(
            f"Pinecone index '{index_name}' does not exist. Please create it in the Pinecone console."
        )
    else:
        print('Index exists:', index_name)

def upsert_vectors(vectors: List[tuple]):
    """Upsert vectors to Pinecone index."""
    index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

    print('Index in upsert_vectors:  ', index)
    
    # Prepare vectors for upserting
    vectors_to_upsert = []
    for i, (text, embedding) in enumerate(vectors):
        vectors_to_upsert.append({
            "id": f"chunk_{i}",
            "values": embedding,
            "metadata": {"text": text}
        })
    
    print('\n\nVectors to upsert:', vectors_to_upsert)
    # Upsert in batches of 100
    batch_size = 100
    for i in range(0, len(vectors_to_upsert), batch_size):
        batch = vectors_to_upsert[i:i + batch_size]
        index.upsert(vectors=batch)
    
    print('\n\nVectors upserted:', vectors_to_upsert)

def query_similar_chunks(query_embedding: List[float], top_k: int = 5) -> List[Dict]:
    """Query Pinecone for similar chunks."""
    index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
    
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )
    
    return results.matches 