import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Chat with your PDF", layout="wide")
st.title("📄 Chat with your PDF using RAG")

# File uploader
uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file is not None:
    with st.spinner("Uploading and processing PDF..."):
        files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
        res = requests.post(f"{API_URL}/upload_pdf/", files=files)
        if res.status_code == 200:
            st.success("PDF uploaded and processed!")
        else:
            st.error("Failed to process PDF")

# Conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat input
if question := st.chat_input("Ask something about the PDF..."):
    st.session_state.messages.append({"role": "user", "content": question})
    response = requests.post(f"{API_URL}/ask_question/", json={"question": question})
    if response.status_code == 200:
        answer = response.json().get("answer")
        st.session_state.messages.append({"role": "assistant", "content": answer})
    else:
        st.error("Error querying the PDF.")

# Render chat history
st.subheader("Chat History")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
