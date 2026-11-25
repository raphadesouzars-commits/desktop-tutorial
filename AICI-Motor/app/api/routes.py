"""API do AICI-Motor: /upload, /analisar, /gerar-parecer, /indicadores (+ /indexar, /revisar, /categorias, /saude)."""
from __future__ import annotations

import hmac
import os

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse

from ..models.schemas import Analise, Minuta, PedidoAnalise, PedidoParecer
from ..services.analysis_service import ErroNegocio, Motor

DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def criar_router(motor: Motor) -> APIRouter:
    token_env = motor.s.get("servidor.token_env", "AICI_TOKEN")

    def autenticar(x_aici_token: str = Header(default="")):
        esperado = os.environ.get(token_env, "")
        if esperado and not hmac.compare_digest(esperado, x_aici_token):
            raise HTTPException(401, "Token inválido ou ausente (cabeçalho X-AICI-Token).")

    r = APIRouter(dependencies=[Depends(autenticar)])

    def erro(e: ErroNegocio):
        return HTTPException(e.status, str(e))

    @r.get("/saude")
    def saude():
        return {"status": "ok", "provider": motor.provider.nome, "indice": motor.store.contagem(), "backend": motor.store.nome,
                "arquivos_indexados": len(motor.store.manifesto),
                "embeddings": motor.embedder.nome if motor.embedder else None,
                "ocr": __import__("app.services.ocr_service", fromlist=["x"]).ocr_disponivel()}

    @r.post("/upload")
    async def upload(arquivo: UploadFile = File(...), usuario: str = Form("")):
        dados = await arquivo.read(25 * 1024 * 1024 + 1)
        try:
            return motor.receber_pdf(arquivo.filename or "consulta.pdf", dados, usuario)
        except ErroNegocio as e:
            raise erro(e)

    @r.post("/analisar", response_model=Analise)
    def analisar(p: PedidoAnalise):
        try:
            return motor.analisar(p.consulta_id, p.gerar_minuta)
        except ErroNegocio as e:
            raise erro(e)

    @r.post("/gerar-parecer")
    def gerar(p: PedidoParecer):
        try:
            caminho, nome = motor.gerar_documento(p)
        except ErroNegocio as e:
            raise erro(e)
        return FileResponse(caminho, media_type=DOCX, filename=nome)

    @r.post("/minuta", response_model=Minuta)
    def minuta(p: PedidoParecer):
        try:
            return motor.nova_minuta(p)
        except ErroNegocio as e:
            raise erro(e)

    @r.post("/revisar")
    def revisar(consulta_id: int, minuta: Minuta):
        try:
            return {"pontos": motor.revisar(consulta_id, minuta)}
        except ErroNegocio as e:
            raise erro(e)

    @r.get("/indicadores")
    def indicadores():
        return motor.metricas.indicadores()

    @r.post("/indexar")
    def indexar(completo: bool = False):
        return motor.indexar(completo)

    @r.get("/categorias")
    def categorias():
        return [{"id": c["id"], "nome": c["nome"], "grupo": c.get("grupo", ""),
                 "variantes": [{"id": v["id"], "rotulo": v["rotulo"], "resultado": v["resultado"]} for v in c["variantes"]]}
                for c in motor.classificador.cats.values()]

    return r
