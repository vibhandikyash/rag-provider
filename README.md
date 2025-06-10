# Document Q&A System

This system allows you to ask questions about your PDF documents using natural language. It uses OpenAI's embeddings and Pinecone vector database to find relevant information from your documents.

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with the following variables:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   PINECONE_API_KEY=your_pinecone_api_key_here
   PINECONE_ENVIRONMENT=your_pinecone_environment_here
   PINECONE_INDEX_NAME=your_index_name_here
   ```

## Usage

1. Place your PDF documents in the `data/` directory

2. Process and upload embeddings to Pinecone:

   ```bash
   python embeddings/upload_to_pinecone.py
   ```

3. Start the FastAPI backend:

   ```bash
   cd api
   uvicorn main:app --reload
   ```

4. In a new terminal, start the Streamlit frontend:

   ```bash
   cd streamlit_app
   streamlit run app.py
   ```

5. Open your browser and navigate to `http://localhost:8501`

## Project Structure

```
your_project/
├── data/                         # Contains PDF files to embed
├── embeddings/
│   └── upload_to_pinecone.py     # Script to process and upload vectors
├── api/
│   ├── main.py                   # FastAPI app
│   ├── embedding_utils.py        # Embedding & chunking logic
│   ├── pinecone_utils.py         # Pinecone querying logic
├── streamlit_app/
│   └── app.py                    # Streamlit frontend for chat
├── .env                          # API keys and config
├── requirements.txt              # All required dependencies
└── README.md                     # Documentation for setup and usage
```

## Features

- PDF text extraction and chunking
- OpenAI embeddings generation
- Pinecone vector database integration
- FastAPI backend for querying
- Streamlit chat interface
- Real-time document Q&A

## Requirements

- Python 3.8+
- OpenAI API key
- Pinecone API key
- PDF documents to query
