import os, time
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from smart_uae_agent import build_agent

LLM_BACKEND = os.getenv("SMARTUAE_LLM", "openai")
KB_PATH = os.getenv("SMARTUAE_KB", "uae_knowledge.json")
os.environ.setdefault("USE_ALADHAN_API", "false")

try:
    agent = build_agent(KB_PATH, LLM_BACKEND)
except Exception as e:
    raise

app = FastAPI(title="SmartUAE Tourism Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

class ChatIn(BaseModel):
    message: str
    llm: Optional[str] = None
    kb: Optional[str] = None

class ChatOut(BaseModel):
    output: str
    latency_ms: int

@app.get("/")
def root():
    return {"ok": True, "endpoints": {"GET /healthz": {}, "POST /chat": {"body":{"message":"string"}}}}

@app.get("/healthz")
def health():
    return {"ok": True, "llm": LLM_BACKEND, "kb": KB_PATH}

@app.post("/chat", response_model=ChatOut)
def chat(body: ChatIn):
    global agent
    msg = (body.message or "").strip()
    if not msg:
        raise HTTPException(status_code=400, detail="message is required")
    if body.llm or body.kb:
        agent = build_agent(body.kb or KB_PATH, body.llm or LLM_BACKEND)
    t0 = time.time()
    try:
        resp = agent.invoke({"input": msg})
        out = resp.get("output") or str(resp)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return ChatOut(output=out, latency_ms=int((time.time() - t0) * 1000))
