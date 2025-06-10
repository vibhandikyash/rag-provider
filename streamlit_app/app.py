import streamlit as st
import requests
import json

# Configure the page
st.set_page_config(
    page_title="Document Q&A System",
    page_icon="📚",
    layout="wide"
)

# Title and description
st.title("📚 Document Q&A System")
st.markdown("""
This application allows you to ask questions about your documents. 
The system will search through the documents and provide relevant answers based on the context.
""")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about your documents"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response from API
    try:
        response = requests.post(
            "http://localhost:8000/query",
            json={"text": prompt}
        )
        response.raise_for_status()
        results = response.json()["results"]

        # Format the response
        if results:
            answer = "Based on the documents, here are the relevant passages:\n\n"
            for i, result in enumerate(results, 1):
                answer += f"{i}. {result['text']}\n\n"
        else:
            answer = "I couldn't find any relevant information in the documents."

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)

    except Exception as e:
        error_message = f"Error: {str(e)}"
        st.session_state.messages.append({"role": "assistant", "content": error_message})
        with st.chat_message("assistant"):
            st.markdown(error_message) 