import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Chat with your PDF", layout="wide")
st.title("📄 Chat with your PDF using RAG")

# File uploader
uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file is not None:
    with st.spinner("Processing..."):
        files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
        res = requests.post(f"{API_URL}/upload_pdf/", files=files)
        if res.status_code == 200:
            st.success("PDF uploaded and processed!")
            st.session_state["pdf_uploaded"] = True
        else:
            st.error(f"Failed to process PDF: {res.text}")
            st.session_state["pdf_uploaded"] = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


question = st.text_input("Ask a question about the PDF:")
ask_btn = st.button("💡 Ask ")
if ask_btn:
    if not question:
        st.error("Please enter a question.")
    elif not st.session_state.get("pdf_uploaded", False):
        st.warning("Please upload and process a PDF first.")
    else:
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        response = requests.post(f"{API_URL}/ask_question/", json={"question": question})
        if response.status_code == 200:
            answer = response.json().get("answer")
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            with st.chat_message("assistant"):
                    st.markdown(answer)
        else:
            st.error(f"Error querying the PDF: {response.text}")

ask_btn_with_sources = st.button("💡Ask with Sources")
if ask_btn_with_sources:
    if not question:
        st.error("Please enter a question.")
    elif not st.session_state.get("pdf_uploaded", False):
        st.warning("Please upload and process a PDF first.")
    else:
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        response = requests.post(f"{API_URL}/ask_question/", json={"question": question})
        if response.status_code == 200:
            answer = response.json().get("answer")
            sources = response.json().get("sources")
            final_answer = answer+"\n\nSources: "+str(sources)
            st.session_state.chat_history.append({"role": "assistant", "content": final_answer})
            with st.chat_message("assistant"):
                    st.markdown(final_answer)
        else:
            st.error(f"Error querying the PDF: {response.text}")


st.subheader("Chat History")
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


