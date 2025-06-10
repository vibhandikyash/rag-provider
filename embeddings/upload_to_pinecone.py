import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import from api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.embedding_utils import process_pdf_files
from api.pinecone_utils import init_pinecone, create_index_if_not_exists, upsert_vectors

def main():
    load_dotenv()
    
    # Initialize Pinecone
    init_pinecone()
    # create_index_if_not_exists()
    
    # Process PDFs and get embeddings
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    vectors = process_pdf_files(data_dir)
    
    # Upload to Pinecone
    print(f"\nUploading {len(vectors)} vectors to Pinecone...\n")
    upsert_vectors(vectors)
    print("\nUpload complete!")

if __name__ == "__main__":
    main() 