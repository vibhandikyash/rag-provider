import streamlit as st
import requests
import logging
from typing import Dict, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8001")
PROVIDER_ID = "33151"  # You can make this configurable

def get_chat_response(user_query: str) -> str:
    """Get chat response from the backend API"""
    try:
        logger.info(f"Calling chat API with query: {user_query}")
        api_url = f"{API_BASE_URL}/api/v1/chat"
        payload = {
            "user_query": user_query,
            "provider_id": PROVIDER_ID
        }
        
        response = requests.post(api_url, json=payload)   
        data = response.json()
      
        return data["response"]
        
    except requests.exceptions.Timeout:
        logger.error("API request timed out")
        return "The request is taking longer than expected. Please try again."
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling chat API: {str(e)}")
        return "I'm having trouble connecting to the service. Please try again later."
    except Exception as e:
        logger.error(f"Unexpected error getting chat response: {str(e)}")
        return "An unexpected error occurred. Please try again."

# Streamlit UI Setup
st.set_page_config(
    page_title="BigToe AI Assistant", 
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for centering and styling
st.markdown("""
    <style>
    .stApp {
        max-width: 800px;
        margin: 0 auto;
        padding: 1rem;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 10rem;
    }
    .st-emotion-cache-10trblm {
        text-align: center;
    }
    .st-emotion-cache-1629p8f {
        margin: 0 auto;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 BigToe AI Assistant")
st.markdown("---")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Get initial greeting and add it to chat history
    with st.spinner("Initializing..."):
        initial_greeting = get_chat_response("")
    st.session_state.messages.append({"role": "assistant", "content": initial_greeting})

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What would you like to know about BigToe?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response from backend API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_chat_response(prompt)
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
    
