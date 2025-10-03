from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn
import os
import shutil
import tempfile
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.llms import HuggingFaceHub
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import ChatOllama
from langchain.chains import RetrievalQA
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_community.chat_models import ChatOllama
from langchain.retrievers.multi_query import MultiQueryRetriever
from fastapi.responses import StreamingResponse
import asyncio

retriever = None
qa_chain = None

app = FastAPI(title="RAG PDF Chat API")

# Allow CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text_from_pdf(pdf_path: str) -> str:
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()   # returns a list of Document objects (often one per page)
    print(f"Loaded {len(docs)} documents (often page-level).")
    return docs


def build_vectorstore(docs: str,pdf_path:str):
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200)
    chunk_docs = []
    for i, d in enumerate(docs):
        pieces = splitter.split_text(d.page_content)
        for j, p in enumerate(pieces):
            md = dict(d.metadata) if d.metadata else {}
            md.update({"source": pdf_path, "orig_page": i, "chunk": j})
            chunk_docs.append(Document(page_content=p, metadata=md))
    print("Total chunks created:", len(chunk_docs))
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    print(f"Using HuggingFace embeddings: {model_name}")
    persist_directory = "./chroma_db"   # change if you want another folder
    vectordb = Chroma.from_documents(documents=chunk_docs, embedding=embeddings,
                                 persist_directory=persist_directory)
    return vectordb

def format_docs(docs):
  return "\n".join(doc.page_content for doc in docs)

def build_chain(vectordb):
    global qa_chain
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    print(f"Using HuggingFace embeddings: {model_name}")
    try:
        vectordb.persist()
    except Exception as e:
        print("Persist not available / failed:", e)

    retriever = vectordb.as_retriever(search_kwargs={"k": 4})
    print("Vector DB ready. Retriever k=3")
    llm = ChatOllama(model="llama3.2:1b",streaming=True,num_predict=256)
    prompt = hub.pull("rlm/rag-prompt")
    multi_q = MultiQueryRetriever.from_llm(
    retriever,
    llm=llm,
    include_original=True)
    compressor = LLMChainExtractor.from_llm(llm)
    cc_retriever = ContextualCompressionRetriever(
    base_retriever= multi_q,
    base_compressor=compressor)
    rag_chain = (
    {"context": cc_retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | (lambda x: str(x))  # Explicitly convert prompt output to string
    | llm
    | StrOutputParser())


    return rag_chain


@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    global retriever, qa_chain

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    text = extract_text_from_pdf(tmp_path)
    vectorstore = build_vectorstore(text,tmp_path)
    qa_chain = build_chain(vectorstore)

    return {"message": "PDF processed successfully. You can now ask questions."}

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask_question/")
async def ask_question(req: QuestionRequest):
    global qa_chain
    if qa_chain is None:
        return {"error": "Please upload a PDF first."}

    result = qa_chain.invoke(req.question)
    return {"answer": result}

@app.post("/ask_question_stream/")
async def ask_question_stream(req: QuestionRequest):
   global qa_chain
   if qa_chain is None:
       return StreamingResponse(iter(["Please upload a PDF first."]), media_type="text/plain")


   async def generate():
      result = qa_chain.invoke(req.question)
      for token in list(result):
            yield token
            await asyncio.sleep(0.02) # simulate token-level delay


   return StreamingResponse(generate(), media_type="text/plain")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)