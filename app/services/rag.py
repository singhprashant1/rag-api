import os

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI        # was: ChatOpenAI


from app.services.ingestion import get_embeddings, CHROMA_DIR

load_dotenv()

PROMPT = ChatPromptTemplate.from_template(
    """Answer the question using only the context below.
If the answer is not in the context, say you don't know.

Context:
{context}

Question: {question}
"""
)


def get_vectorstore():
    return Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=get_embeddings(),
    )


def ask_question(question: str):
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    docs = retriever.invoke(question)
    context = "\n\n".join(doc.page_content for doc in docs)

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        temperature=0,
        google_api_key=os.environ["GEMINI_API_KEY"],
    )
    messages = PROMPT.format_messages(context=context, question=question)
    response = llm.invoke(messages)

    return response.content