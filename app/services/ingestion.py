import os

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings   # was: langchain_openai


load_dotenv()

DOCUMENTS_DIR = "documents"
CHROMA_DIR = "chroma_db"


def load_pdf(file_path: str):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    return documents


def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = splitter.split_documents(documents)
    return chunks


def get_embeddings():
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",          # <- from step 3
        google_api_key=os.environ["GEMINI_API_KEY"],
    )


def ingest_documents():
    all_chunks = []

    for file_name in os.listdir(DOCUMENTS_DIR):
        if not file_name.lower().endswith(".pdf"):
            continue

        file_path = os.path.join(DOCUMENTS_DIR, file_name)
        documents = load_pdf(file_path)
        chunks = split_documents(documents)
        all_chunks.extend(chunks)

    if not all_chunks:
        return 0

    Chroma.from_documents(
        documents=all_chunks,
        embedding=get_embeddings(),
        persist_directory=CHROMA_DIR,
    )

    return len(all_chunks)