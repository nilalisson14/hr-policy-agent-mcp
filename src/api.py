"""
API HTTP sobre o motor de consulta de políticas de RH.

Não substitui o servidor MCP (mcp_server.py) — essa API existe apenas para
permitir que o site (PHP, via HTTP) mostre uma demonstração ao vivo do
projeto. O MCP continua sendo a peça que expõe o agente para hosts
compatíveis (Claude Desktop, outros agentes).

Rodar localmente:
    uvicorn api:app --host 0.0.0.0 --port 8000

Rodar em produção (VPS), ver README_DEPLOY.md para systemd + nginx.
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from query_engine import PolicyQueryEngine

app = FastAPI(title="HR Policy Agent — Demo API")

# Restrinja para o domínio do seu site em produção.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("ALLOWED_ORIGIN", "https://nilalisson.com.br")],
    allow_methods=["POST"],
    allow_headers=["*"],
)

engine: PolicyQueryEngine | None = None


@app.on_event("startup")
def load_engine() -> None:
    global engine
    engine = PolicyQueryEngine()


class ConsultaRequest(BaseModel):
    tema: str


@app.post("/consultar")
def consultar(req: ConsultaRequest):
    if engine is None:
        raise HTTPException(status_code=503, detail="Engine ainda não carregado")
    if not req.tema.strip():
        raise HTTPException(status_code=400, detail="Tema vazio")
    return engine.consultar_politica(req.tema)


@app.get("/health")
def health():
    return {"status": "ok"}
