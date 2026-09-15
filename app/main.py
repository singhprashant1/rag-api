from fastapi import FastAPI


app = FastAPI(
    title="RAG API",
    version="1.0.0"
)

@app.get("/")

def root():
    return {
        "message": "RAG API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }