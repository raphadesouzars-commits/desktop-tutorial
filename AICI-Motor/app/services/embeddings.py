"""Embeddings locais para a busca semântica (HybridRetriever = BM25 + vetores). Opcional: desligado por padrão.
Modelos recomendados para português jurídico: BAAI/bge-m3 ou intfloat/multilingual-e5-large, rodando LOCALMENTE
(baixe uma vez numa máquina com internet e aponte `modelo` para a pasta; nada do acervo sai da rede)."""
from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from pathlib import Path


class Embedder(ABC):
    nome = "base"

    @abstractmethod
    def embed_documentos(self, textos: list[str]) -> list[list[float]]: ...

    @abstractmethod
    def embed_consulta(self, texto: str) -> list[float]: ...


class SentenceTransformerEmbedder(Embedder):
    """Requer `pip install sentence-transformers`. Para e5, use prefixo_consulta "query: " e prefixo_documento "passage: "."""

    def __init__(self, modelo: str, prefixo_consulta: str = "", prefixo_documento: str = "", dispositivo: str = "cpu", lote: int = 16):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as e:
            raise RuntimeError("sentence-transformers não instalado (requirements-opcional.txt)") from e
        self.nome = f"st:{modelo}"
        self.m = SentenceTransformer(modelo, device=dispositivo)
        self.pq, self.pd, self.lote = prefixo_consulta, prefixo_documento, lote

    def embed_documentos(self, textos):
        return self.m.encode([self.pd + t for t in textos], normalize_embeddings=True, batch_size=self.lote,
                             show_progress_bar=False).tolist()

    def embed_consulta(self, texto):
        return self.m.encode([self.pq + texto], normalize_embeddings=True, show_progress_bar=False)[0].tolist()


def criar_embedder(settings) -> Embedder | None:
    cfg = settings.get("recuperacao.embeddings", {}) or {}
    if not cfg.get("habilitado"):
        return None
    return SentenceTransformerEmbedder(cfg.get("modelo", "BAAI/bge-m3"), cfg.get("prefixo_consulta", ""),
                                       cfg.get("prefixo_documento", ""), cfg.get("dispositivo", "cpu"))


def _chave(c) -> str:
    return f"{c.id}|{hashlib.sha1(c.texto.encode('utf8')).hexdigest()[:12]}"


class DenseStore:
    """Vetores dos trechos em vectorstore/dense.npy (+ dense_chaves.json). Incremental: só embute trechos novos ou alterados."""

    def __init__(self, pasta: Path):
        import numpy as np
        self.np = np
        self.arq_m, self.arq_k = Path(pasta) / "dense.npy", Path(pasta) / "dense_chaves.json"
        self.chaves: list[str] = []
        self.mat = None
        if self.arq_m.exists() and self.arq_k.exists():
            self.chaves = json.loads(self.arq_k.read_text(encoding="utf8"))
            self.mat = np.load(self.arq_m)

    def sincronizar(self, chunks, embedder: Embedder, lote: int = 64) -> dict:
        np = self.np
        atual = {k: i for i, k in enumerate(self.chaves)}
        alvo = [_chave(c) for c in chunks]
        novos = [(k, c) for k, c in zip(alvo, chunks) if k not in atual]
        vetores = []
        for i in range(0, len(novos), lote):
            vetores += embedder.embed_documentos([c.titulo + ". " + c.texto for _, c in novos[i:i + lote]])
        novos_m = {k: v for (k, _), v in zip(novos, vetores)}
        linhas = [self.mat[atual[k]] if k in atual else np.asarray(novos_m[k], dtype="float32") for k in alvo]
        self.mat = np.vstack(linhas).astype("float32") if linhas else np.zeros((0, 1), dtype="float32")
        self.chaves = alvo
        self.arq_m.parent.mkdir(parents=True, exist_ok=True)
        np.save(self.arq_m, self.mat)
        self.arq_k.write_text(json.dumps(alvo), encoding="utf8")
        return {"vetores": len(alvo), "novos": len(novos)}

    def buscar(self, vetor, permitidos: dict[str, object], n: int) -> list[tuple[str, float]]:
        """permitidos: {chave: chunk} já filtrado por tipo. Devolve [(chave, similaridade)]."""
        np = self.np
        if self.mat is None or not len(self.chaves):
            return []
        sims = self.mat @ np.asarray(vetor, dtype="float32")
        idx = [i for i, k in enumerate(self.chaves) if k in permitidos]
        idx.sort(key=lambda i: -float(sims[i]))
        return [(self.chaves[i], float(sims[i])) for i in idx[:n]]
