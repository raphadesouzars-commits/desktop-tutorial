"""AICI-Motor - Assistente Inteligente para Conflitos de Interesse (COGER/RFB).
Executar:  python main.py   (ou: uvicorn main:app --host 127.0.0.1 --port 8765)"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import criar_router
from app.config import carregar
from app.services.analysis_service import Motor


def criar_app(settings=None, provider=None, indexar_ao_iniciar: bool = True) -> FastAPI:
    s = settings or carregar()
    motor = Motor(s, provider=provider)

    @asynccontextmanager
    async def vida(_):
        if indexar_ao_iniciar:
            motor.indexar()          # incremental: só reprocessa o que mudou em knowledge/
        yield

    app = FastAPI(title="AICI-Motor", version="0.1.0", lifespan=vida,
                  description="Motor de apoio à análise de conflito de interesses: PDF -> fatos -> conhecimento -> minuta.")
    app.add_middleware(CORSMiddleware, allow_origins=s.get("servidor.cors_origens", []), allow_methods=["GET", "POST"],
                       allow_headers=["Content-Type", "X-AICI-Token"], expose_headers=["Content-Disposition"])

    @app.middleware("http")
    async def rede_privada(request: Request, call_next):   # HTML aberto como arquivo -> localhost (Private Network Access)
        resp = await call_next(request)
        if request.headers.get("access-control-request-private-network"):
            resp.headers["Access-Control-Allow-Private-Network"] = "true"
        return resp

    app.include_router(criar_router(motor))
    app.state.motor = motor
    return app


app = criar_app()

if __name__ == "__main__":
    import uvicorn
    cfg = carregar()
    uvicorn.run("main:app", host=cfg.get("servidor.host", "127.0.0.1"), port=int(cfg.get("servidor.porta", 8765)))
