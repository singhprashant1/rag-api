from fastapi import APIRouter

from app.models.schema import QuestionRequest
from app.services.rag import ask_question
from app.services.ingestion import ingest_documents


router = APIRouter()


@router.post("/ingest")
def ingest():
    count = ingest_documents()
    return {"chunks_indexed": count}


@router.post("/chat")
def chat(request: QuestionRequest):
    answer = ask_question(request.question)
    return {"answer": answer}