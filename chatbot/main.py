import os
import time
import logging
import uuid
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from rag import chat

load_dotenv()

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("chatbot")

# ── Config ────────────────────────────────────────────────────────────────────
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
RATE_LIMIT = os.getenv("RATE_LIMIT", "30/minute")
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",")]

# ── Rate Limiter ──────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=[RATE_LIMIT])


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Akshat Chatbot API starting up...")
    yield
    logger.info("Akshat Chatbot API shutting down.")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Akshat Portfolio Chatbot API",
    description="RAG-powered AI assistant for Akshat Jain's portfolio",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url=None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)


# ── Middleware: request logging + timing ──────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    req_id = str(uuid.uuid4())[:8]
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 1)
    logger.info(f"[{req_id}] {request.method} {request.url.path} → {response.status_code} ({duration}ms)")
    return response


# ── Schemas ───────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Message cannot be empty.")
        if len(v) > 500:
            raise ValueError("Message too long. Max 500 characters.")
        return v


class ChatResponse(BaseModel):
    type: str
    message: str
    whatsapp_url: str | None = None
    session_id: str
    timestamp: float


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Status"])
def root():
    return {
        "status": "online",
        "service": "Akshat Portfolio Chatbot API",
        "version": "2.0.0",
    }


@app.get("/health", tags=["Status"])
def health():
    return {
        "status": "healthy",
        "uptime": "ok",
        "rag": "loaded",
    }


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
@limiter.limit(RATE_LIMIT)
async def chat_endpoint(request: Request, req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())
    logger.info(f"[session:{session_id[:8]}] User: {req.message[:80]}")

    try:
        result = chat(req.message, session_id=session_id)
    except Exception as e:
        logger.error(f"RAG error: {e}")
        raise HTTPException(status_code=500, detail="Internal error. Please try again.")

    logger.info(f"[session:{session_id[:8]}] Bot ({result['type']}): {result['message'][:80]}")

    return ChatResponse(
        type=result["type"],
        message=result["message"],
        whatsapp_url=result.get("whatsapp_url"),
        session_id=session_id,
        timestamp=time.time(),
    )


@app.exception_handler(422)
async def validation_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid request. Check your message field."},
    )
