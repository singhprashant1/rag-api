import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from google.api_core import exceptions as gexc
from app.api.routes.chat import router as chat_router

log = logging.getLogger(__name__)




app = FastAPI(
    title="RAG API",
    version="1.0.0"
)

app.include_router(
    chat_router,
    prefix="/api"
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



def _handler(status: int, detail: str):
    async def h(request, exc):
        log.error("Gemini call failed: %s", exc)
        return JSONResponse(status_code=status, content={"detail": detail})
    return h

# narrow types first — Starlette walks the MRO, so the base must be registered last
app.add_exception_handler(gexc.ResourceExhausted,  _handler(429, "Gemini quota or rate limit reached. Retry shortly."))
app.add_exception_handler(gexc.Unauthenticated,    _handler(500, "Gemini credentials rejected. Check GEMINI_API_KEY."))
app.add_exception_handler(gexc.PermissionDenied,   _handler(500, "Gemini credentials rejected. Check GEMINI_API_KEY."))
app.add_exception_handler(gexc.DeadlineExceeded,   _handler(504, "Gemini request timed out."))
app.add_exception_handler(gexc.ServiceUnavailable, _handler(504, "Gemini is unreachable."))
app.add_exception_handler(gexc.GoogleAPICallError, _handler(502, "Upstream Gemini error."))