import streamlit as st
import requests

API_URL = "http://localhost:8000"

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
        else:
            st.error("Failed to process PDF")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


question = st.text_input("Ask a question about the PDF:")


if st.button("Ask with Streaming"):
    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        response = requests.post(f"{API_URL}/ask_question_stream/", json={"question": question}, stream=True)
        if response.status_code == 200:
            answer_placeholder = st.empty()
            answer = ""

            with st.chat_message("assistant"):
                for chunk in response.iter_content(chunk_size=1, decode_unicode=True):
                    answer += chunk
                    answer_placeholder.markdown(f"**PDF Bot:** {answer}")
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
    else:
        st.error("Error querying the PDF.")
elif st.button("Ask"):
    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        response = requests.post(f"{API_URL}/ask_question/", json={"question": question})
        if response.status_code == 200:
            answer = response.json().get("answer")
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
        else:
            st.error("Error querying the PDF.")


st.subheader("Chat History")
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        st.markdown("---")


