import logging
from typing import Any, Dict, List
import fitz
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv
# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()
class InvoiceProcessor:
    def __init__(self, model_name: str = "gpt-4o"):  # do not change the model name
        """
        Initialize the Invoice Processor with the specified model.

        Args:
            model_name: The name of the OpenAI model to use
        """
        # Initialize OpenAI components
        self.model_name = model_name
        self.llm = ChatOpenAI(model_name=model_name, temperature=0)
        self.embeddings = OpenAIEmbeddings()
        
        # Initialize sentence transformer for vectorization
        # self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        
        
        # File storage paths
        self.index_file = "big_toe_index.index"
        self.chunks_file = "big_toe_chunks.npy"
        
        # Vector store and documents
        self.vector_store = None
        self.index = None
        self.chunks = []
        
        logger.info(f"Initialized InvoiceProcessor with model: {model_name}")

    def read_and_chunk_file(self, pdf_path: str) -> List[Document]:
        """
        Read a PDF file and chunk it into smaller documents using the fitz (PyMuPDF) library.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            List of document chunks as Document objects.
        """
        logger.info(f"Reading PDF file: {pdf_path}")
        doc = fitz.open(pdf_path)
        text_content = ""
        
        # Extract text from all pages
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            text_content += text
        
        # Split text into meaningful chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Create Document objects
        chunks = []
        texts = text_splitter.split_text(text_content)

        print("texts in read_and_chunk_method: ", texts)
        
        for i, text_chunk in enumerate(texts):
            if text_chunk.strip():
                chunks.append(Document(
                    page_content=text_chunk.strip(),
                    metadata={"source": pdf_path, "chunk_id": i}
                ))

        print("chunks in read_and_chunk_method: ", chunks)
        
        logger.info(f"Created {len(chunks)} document chunks from PDF")
        return chunks

    def create_index(self, chunks: List[Document]) -> FAISS:
        """
        Create a vector index from document chunks.

        Args:
            chunks: List of document chunks

        Returns:
            FAISS vector store
        """
        logger.info("Creating FAISS index from document chunks")
        
        if not chunks:
            logger.warning("No chunks provided to create index")
            return None
            
        # Create FAISS index using LangChain's FAISS wrapper
        vector_store = FAISS.from_documents(chunks, OpenAIEmbeddings())
        
        # Save the vector store for later use
        self.vector_store = vector_store
        self.chunks = chunks
        
        logger.info(f"FAISS index created successfully with {len(chunks)} chunks")
        return vector_store

    def retrieve_top_chunks(self, query: str, k: int = 5) -> List[Document]:
        """
        Retrieve the top k relevant document chunks for a given query using semantic search.

        Args:
            query: The query to search for
            k: Number of chunks to retrieve

        Returns:
            List of relevant document chunks

        Raises:
            ValueError: If the index does not exist.
        """
        logger.info(f"Retrieving top {k} chunks for query: {query}")
        
        if self.vector_store is None:
            raise ValueError("No index available. Process an invoice first.")
        
        # Use semantic search with similarity threshold
        retrieved_docs = self.vector_store.similarity_search_with_score(
            query,
            k=k
        )
        
        # Filter and sort by relevance
        relevant_docs = []
        for doc, score in retrieved_docs:
            # Convert score to similarity (FAISS returns distance, smaller is better)
            similarity = 1 / (1 + score)
            if similarity > 0.3:  # Adjust threshold as needed
                relevant_docs.append(doc)
        
        logger.info(f"Retrieved {len(relevant_docs)} relevant chunks with semantic search")
        return relevant_docs

    def generate_answer(self, query: str) -> Dict[str, Any]:
        """
        Generate an answer to a query using the RAG system.

        Args:
            query: The query to answer.

        Returns:
            Dictionary containing:
            - "answer": The generated answer.
            - "source_chunks": The relevant document chunks used to generate the answer.

        Raises:
            ValueError: If the index does not exist.
        """
        logger.info(f"Generating answer for query: {query}")
        
        # Retrieve relevant chunks
        source_chunks = self.retrieve_top_chunks(query)
        
        if not source_chunks:
            return {
                "answer": "I couldn't find relevant information to answer this query.",
                "source_chunks": []
            }
        
        # Create context from retrieved chunks
        context = "\n\n".join([chunk.page_content for chunk in source_chunks])
        
        print("context in generate_answer method: ", context)
        
        # Create prompt template
        prompt_template = """
        You are an AI assistant specialized in extracting information from invoices.
        
        Use the following pieces of context to answer the user's question.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        Keep the answer concise and directly address the question.
        
        Context:
        {context}
        
        Question: {question}
        
        Answer:
        """
        
        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )
        
        # Create retrieval QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT},
            retriever=self.vector_store.as_retriever()
        )
        
        # Generate response
        response = qa_chain({"query": query})
        
        result = {
            "answer": response["result"],
            "source_chunks": [doc.page_content for doc in source_chunks]
        }
        
        logger.info("Answer generated successfully")
        return result

    def process_invoice(self, pdf_path: str) -> bool:
        """
        Process an invoice PDF and prepare for querying.

        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Boolean indicating success
        """
        logger.info(f"Processing invoice: {pdf_path}")
        try:
            # Read and chunk the PDF
            chunks = self.read_and_chunk_file(pdf_path)
            
            if not chunks:
                logger.error("No content extracted from PDF")
                return False
                
            # Create the index
            self.vector_store = self.create_index(chunks)
            if self.vector_store is None:
                logger.error("Failed to create vector store")
                return False
                
            logger.info(f"Successfully processed invoice: {pdf_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing invoice: {e}")
            return False

    def answer_invoice_query(self, query: str) -> Dict[str, Any]:
        """
        Answer a query about the processed invoice.

        Args:
            query: The query to answer

        Returns:
            Dictionary containing the answer and source chunks
            {
                "answer": "answer",
                "source_chunks": "source_chunks"
            }
        """
        logger.info(f"Answering invoice query: {query}")
        try:
            result = self.generate_answer(query)
            print("result in answer_invoice_query method: pv", result)
            return result
        except Exception as e:
            logger.error(f"Error answering query: {e}")
            return {
                "answer": f"Error processing your query: {str(e)}",
                "source_chunks": []
            }


if __name__ == "__main__":
    
    pdf_path = 'C:/Users/Admin/Desktop/Big Toe/data/BigToe_Provider_Knowledge_Base_Detailed.pdf'

    processor = InvoiceProcessor()
    processor.process_invoice(pdf_path)

    sample_queries = [
        "What is big toe?",
    ]

    for query in sample_queries:
        result = processor.answer_invoice_query(query)
        print(f"\nQuery: {query}")
        print(f"Answer: {result['answer']}")