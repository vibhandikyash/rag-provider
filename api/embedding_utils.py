import tiktoken
from typing import List
import openai
from PyPDF2 import PdfReader
import os
from dotenv import load_dotenv
import logging

load_dotenv()

# Set up logging    
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_tokenizer():
    """Get the tokenizer for text chunking."""
    return tiktoken.get_encoding("cl100k_base")

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """Split text into chunks with overlap."""
    tokenizer = get_tokenizer()
    tokens = tokenizer.encode(text)
    chunks = []
    
    i = 0
    while i < len(tokens):
        chunk = tokens[i:i + chunk_size]
        chunks.append(tokenizer.decode(chunk))
        i += chunk_size - chunk_overlap
    
    return chunks

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file."""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def get_embedding(text: str) -> List[float]:
    """Generate embedding for a text using OpenAI's API."""
    logger.info('Text in get_embedding: %s', text)

    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-large"
    )
    
    return response.data[0].embedding

def process_pdf_files(directory: str) -> List[tuple]:
    """Process all PDF files in a directory and return chunks with embeddings."""
    results = []
    print('Processing PDF files in directory:')
    for filename in os.listdir(directory):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(directory, filename)
            print('Processing PDF file:', pdf_path)
            text = extract_text_from_pdf(pdf_path)
            print('Text:', text)
            chunks = chunk_text(text)
            print('Chunks:', chunks)
            
            for chunk in chunks:
                embedding = get_embedding(chunk)
                results.append((chunk, embedding))
    
    return results 