RAG-PDF Chatbot


An open-source Retrieval-Augmented Generation (RAG) chatbot that lets you chat with PDFs.
Upload any PDF and get context-aware, token-streamed answers with citations powered by Ollama LLMs, HuggingFace embeddings, and advanced retrieval techniques like multi-query retriever and contextual compression retriever for higher accuracy and reduced hallucination.

✨ Key Features

📄 PDF Uploads: Upload one or more PDFs and instantly build a searchable knowledge base.

🔍 Multi-Query Retriever: Improves recall by rephrasing queries into multiple semantic variants, capturing diverse perspectives.

✂️ Contextual Compression Retriever: Compresses context chunks to only keep relevant parts, reducing noise and hallucination.

⚡ Token-Level Streaming: Real-time answer generation, mimicking ChatGPT-style streaming.

📝 Source Citations: Every answer shows page numbers and text snippets from the PDF to maintain transparency.

💾 Session Persistence: Keeps chat history and vector indexes for ongoing conversations.

🎨 Elegant UI: Streamlit-powered interface with sidebar controls (model selection, retriever settings, temperature, etc.).

⚙️ Backend + Frontend Separation: FastAPI backend (API endpoints) + Streamlit frontend (chat UI).

How It Works

1. PDF Ingestion

PDFs are uploaded and processed with text extraction + chunking.

Each chunk is embedded using HuggingFace sentence-transformer embeddings and stored in ChromaDB (vector database).

2. Retrieval-Augmented Generation (RAG)

When a user asks a question:

Multi-Query Retriever: Generates multiple reformulated queries to capture more diverse contexts.

Contextual Compression Retriever: Filters and compresses retrieved chunks to keep only the most relevant text.

Context Assembly: Concise and relevant context is passed into the LLM prompt.

3. Answer Generation

Ollama LLMs (open-source large language models) generate the answer.
Streaming enabled → tokens appear in real time.
Retrieved sources (page numbers + text snippets) are shown with the answer.


    Architecture of the Application
            ┌─────────────┐
            │   Streamlit │
            │     (UI)    │
            └──────┬──────┘
                   │
                   ▼
            ┌─────────────┐
            │   FastAPI   │
            │   Backend   │
            └──────┬──────┘
                   │
          ┌──────────────────┐
          │  RAG Components  │
          │LangChain,ChromaDB|
          │,MultiQuery + CCR │
          └────────┬─────────┘
                   │
                   ▼
           ┌───────────────┐
           │    Ollama LLM │
           └───────────────┘

Quickstart
1. Clone the repo
git clone https://github.com/Siri1702/RAG-PDF-Chatbot.git
cd rag-pdf-chatbot

2. Install dependencies
pip install -r requirements.txt

3. Run FastAPI backend
uvicorn app.api:app --host 0.0.0.0 --port 8000 --reload

4. Run Streamlit frontend
streamlit run ui/streamlit_app.py

🔬 Why Multi-Query + Contextual Compression?
Multi-Query Retriever
Normal retrievers often miss relevant chunks because users phrase queries differently. This retriever paraphrases queries into multiple forms, increasing recall and coverage.
Contextual Compression Retriever
Naive retrieval may pass long, irrelevant chunks → bloated prompts and hallucinations.CCR utilizes an LLM to trim chunks down to relevant text only, thereby improving precision and reducing costs.

✅ Together, they provide better accuracy, fewer hallucinations, and more concise answers than standard RAG setups.

🛠️ Tech Stack

Backend: FastAPI, LangChain, ChromaDB
Frontend: Streamlit
Models: Ollama LLMs, HuggingFace Embeddings
