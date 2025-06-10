from fastapi import FastAPI, HTTPException, Header, Cookie
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import openai
import os
from dotenv import load_dotenv
import logging
from embedding_utils import get_embedding
from pinecone_utils import init_pinecone, query_similar_chunks
from provider_auth import get_provider_details, get_initial_message, get_sessions_details
from datetime import datetime

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Pinecone
init_pinecone()

class Query(BaseModel):
    text: str

class ProviderAuth(BaseModel):
    provider_id: str = Field(..., description="Provider ID")
    token: str = Field(..., description="Authentication token")
    type: str = Field(default="provider", description="User type")

class Response(BaseModel):
    results: List[Dict]

class InitialMessageResponse(BaseModel):
    message: str
    provider_details: Optional[Dict] = None

class SessionsResponse(BaseModel):
    sessions: Optional[List[Dict]] = None

@app.post("/query", response_model=Response)
async def query_documents(query: Query):
    try:
        # Generate embedding for the query
        query_embedding = get_embedding(query.text)
        
        # Query Pinecone for similar chunks
        similar_chunks = query_similar_chunks(query_embedding)
        
        # Format results
        results = [
            {
                "text": match.metadata["text"],
                "score": match.score
            }
            for match in similar_chunks
        ]
        
        return Response(results=results)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/initial-message", response_model=InitialMessageResponse)
async def get_initial_chat_message(
    auth: ProviderAuth,
    ci_session: Optional[str] = Cookie(None)
):
    try:
        provider_details = get_provider_details(
            provider_id=auth.provider_id,
            token=auth.token,
            type=auth.type,
            ci_session=ci_session
        )
        # Generate initial message
        message = get_initial_message(provider_details)

        return InitialMessageResponse(
            message=message,
            provider_details=provider_details if provider_details.get("ResponseCode") == 1 else None
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sessions", response_model=SessionsResponse)
async def get_sessions(
    auth: ProviderAuth,
    ci_session: Optional[str] = Cookie(None)
):
    try:
        sessions = get_sessions_details(
            provider_id=auth.provider_id,
            token=auth.token,
            type=auth.type,
            ci_session=ci_session
        )
        
        if sessions.get("ResponseCode") != 1:
            raise HTTPException(status_code=400, detail=sessions.get("ResponseMessage"))
        

        logger.info("return response back")

        result = sessions.get("Result", {})
        
        logger.info("result: %s", len(result))
    

        delivered_sessions = [
            s for s in result
         
        ]

        
        # delivered_sessions.sort(
        #     key=lambda s: datetime.strptime(s["session_confirmed_date"], "%Y-%m-%d"),
        #     reverse=True
        # )

        # Take only `count` sessions
        recent_sessions = delivered_sessions  # delivered_sessions[:5]

        logger.info("return recent sessions")

        return SessionsResponse(
            sessions=recent_sessions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 