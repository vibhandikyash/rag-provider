from pinecone import Pinecone
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

def init_pinecone():
    """Initialize Pinecone client."""
    index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
    return index

def create_index_if_not_exists():
    """Create Pinecone index if it doesn't exist."""
    index_name = os.getenv("PINECONE_INDEX_NAME")
    if index_name not in pc.list_indexes():
        raise RuntimeError(
            f"Pinecone index '{index_name}' does not exist. Please create it in the Pinecone console."
        )

def upsert_vectors(vectors: List[tuple]):
    """Upsert vectors to Pinecone index."""
    index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
    
    # Prepare vectors for upserting
    vectors_to_upsert = []
    for i, (text, embedding) in enumerate(vectors):
        vectors_to_upsert.append({
            "id": f"chunk_{i}",
            "values": embedding,
            "metadata": {"text": text}
        })
    
    # Upsert in batches of 100
    batch_size = 100
    for i in range(0, len(vectors_to_upsert), batch_size):
        batch = vectors_to_upsert[i:i + batch_size]
        index.upsert(vectors=batch)

def query_similar_chunks(query_embedding: List[float], top_k: int = 5) -> List[Dict]:
    """Query Pinecone for similar chunks."""
    index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
    
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )
    
    return results.matches 