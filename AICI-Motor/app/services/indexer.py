"""Módulo 5 - Indexador: ler documentos -> quebrar em chunks -> (embeddings) -> salvar no índice.
Backends: "lexical" (BM25, padrão, offline) e "chroma" (vetorial; requer chromadb e um modelo de embeddings)."""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path

from ..utilities.text import dividir_chunks, tokens

TIPOS = ("pareceres", "precedentes", "normativos", "modelos")
TIPO_SINGULAR = {"pareceres": "parecer", "precedentes": "precedente", "normativos": "normativo", "modelos": "modelo"}


@dataclass
class Chunk:
    id: str
    tipo: str
    titulo: str
    fonte: str
    texto: str
    tema: str = ""
    ano: str = ""
    numero: str = ""
    origem: str = "COGER"
    extra: dict = field(default_factory=dict)


# ---------------------------------------------------------------- leitura de documentos
def ler_documento(arq: Path) -> str:
    ext = arq.suffix.lower()
    if ext == ".pdf":
        import pymupdf as fitz
        with fitz.open(str(arq)) as d:
            return "\n\n".join(p.get_text("text") for p in d)
    if ext == ".docx":
        import docx
        d = docx.Document(str(arq))
        partes = [p.text for p in d.paragraphs if p.text.strip()]
        for t in d.tables:
            for r in t.rows:
                partes.append(" | ".join(c.text.strip() for c in r.cells))
        return "\n\n".join(partes)
    if ext in (".txt", ".md"):
        return arq.read_text(encoding="utf8", errors="replace")
    return ""


def metadados(rel: Path) -> dict:
    """Metadados a partir do caminho/nome. Padrão de nome: PA_<num>_<ano>_<Tema>.ext (a pasta 02_Precedentes tem o tema por subpasta)."""
    nome = rel.stem
    m = re.match(r"(?:PA|PAR)[_ -]?(\d+)[_ -](\d{4})[_ -]?(.*)", nome, re.I)
    meta = {"numero": m.group(1) if m else "", "ano": m.group(2) if m else "", "tema": (m.group(3) if m else "").replace("_", " ")}
    if not meta["tema"] and len(rel.parts) > 2:
        meta["tema"] = rel.parts[-2].replace("_", " ")
    if not meta["ano"] and (a := re.search(r"(20\d{2})", nome)):
        meta["ano"] = a.group(1)
    meta["origem"] = "CGU" if re.search(r"cgu|seci", "/".join(rel.parts), re.I) and rel.parts[0] != "pareceres" else "COGER"
    return meta


def _chunks_modelo_json(arq: Path, rel: str) -> list[Chunk]:
    """Modelos do gerador HTML: um chunk por variante, com a atividade e a origem (PAR/ano) como metadados."""
    m = json.loads(arq.read_text(encoding="utf8"))
    out = []
    for v in m.get("variantes", []):
        corpo = " ".join(b["x"] if isinstance(b["x"], str) else " ".join(b["x"]) for b in v.get("corpo", []))
        texto = f"{m['nome']}. {m.get('descricao','')} {v['rotulo']}. {v.get('quandoUsar','')} {' '.join(v.get('ementa', []))} {corpo}"
        out.append(Chunk(id=f"{rel}#{v['id']}", tipo="modelo", titulo=f"{m['nome']} - {v['rotulo']}", fonte=rel,
                         texto=texto, tema=m.get("grupo", ""), origem="COGER",
                         extra={"atividade_id": m["id"], "variante_id": v["id"], "resultado": v["resultado"],
                                "base": v.get("fonte", "")}))
    return out


def chunks_do_arquivo(raiz: Path, arq: Path, tam: int, sobre: int) -> list[Chunk]:
    rel = arq.relative_to(raiz)
    tipo = TIPO_SINGULAR[rel.parts[0]]
    relstr = rel.as_posix()
    if arq.suffix.lower() == ".json":
        return _chunks_modelo_json(arq, relstr) if tipo == "modelo" else []
    texto = ler_documento(arq)
    if not texto.strip():
        return []
    meta = metadados(rel)
    if arq.name.startswith("CGU_Precedentes"):      # precedentes do SeCI/CGU: um trecho por caso
        return _chunks_cgu(texto, relstr, rel)
    titulo = arq.stem.replace("_", " ")
    cab = f"{titulo}. " if tipo != "normativo" else ""
    return [Chunk(id=f"{relstr}#{i}", tipo=tipo, titulo=titulo, fonte=relstr, texto=cab + c,
                  tema=meta["tema"], ano=meta["ano"], numero=meta["numero"], origem=meta["origem"])
            for i, c in enumerate(dividir_chunks(texto, tam, sobre))]


_CGU = re.compile(r"^Protocolo SeCI nº (\S+) · (\d{4})-\d{2}-\d{2} · ([^·\n]+?) · ([^·\n]+)")


def _chunks_cgu(texto: str, relstr: str, rel: Path) -> list[Chunk]:
    out = []
    for i, bloco in enumerate(b.strip() for b in re.split(r"\n\s*\n", texto)):
        m = _CGU.match(bloco)
        if not m:
            continue
        orgao = re.sub(r"^Secretaria Especial da ", "", m.group(3))
        out.append(Chunk(id=f"{relstr}#{i}", tipo=TIPO_SINGULAR[rel.parts[0]], titulo=f"Precedente CGU/SeCI nº {m.group(1)} ({orgao}; {m.group(4).strip()})",
                         fonte=relstr, texto=bloco, ano=m.group(2), origem="CGU", extra={"unitario": True}))
    return out


def _hash(arq: Path) -> str:
    return hashlib.sha1(arq.read_bytes()).hexdigest()


# ---------------------------------------------------------------- armazenamentos
class LexicalStore:
    """Índice BM25 persistido em vectorstore/lexical.json."""
    nome = "lexical"

    def __init__(self, pasta: Path):
        self.arq = pasta / "lexical.json"
        self.chunks: list[Chunk] = []
        self.manifesto: dict[str, str] = {}
        self._bm = None
        if self.arq.exists():
            d = json.loads(self.arq.read_text(encoding="utf8"))
            self.manifesto = d.get("manifesto", {})
            self.chunks = [Chunk(**c) for c in d.get("chunks", [])]

    def remover_fonte(self, fonte: str):
        self.chunks = [c for c in self.chunks if c.fonte != fonte]; self._bm = None

    def adicionar(self, novos: list[Chunk]):
        self.chunks.extend(novos); self._bm = None

    def salvar(self):
        self.arq.parent.mkdir(parents=True, exist_ok=True)
        self.arq.write_text(json.dumps({"manifesto": self.manifesto, "chunks": [asdict(c) for c in self.chunks]},
                                       ensure_ascii=False), encoding="utf8")

    def limpar(self):
        self.chunks, self.manifesto, self._bm = [], {}, None

    def contagem(self) -> dict:
        r = {}
        for c in self.chunks:
            r[c.tipo] = r.get(c.tipo, 0) + 1
        return r

    def buscar(self, consulta: str, tipo: str | None, n: int) -> list[tuple[Chunk, float, list[str]]]:
        from ..utilities.bm25 import BM25
        if self._bm is None:
            self._bm = BM25([tokens(c.titulo + " " + c.texto) for c in self.chunks])
        q = tokens(consulta)
        sc = self._bm.pontuar(q)
        res = []
        for i, s in sc.items():
            c = self.chunks[i]
            if tipo and c.tipo != tipo:
                continue
            comuns = [t for t in dict.fromkeys(q) if t in self._bm.tf[i]]
            res.append((c, s, comuns))
        res.sort(key=lambda x: -x[1])
        return res[:n]


class ChromaStore:
    """Backend vetorial opcional. Requer `pip install chromadb`. Sem `embedding_function`, o Chroma baixa um modelo
    ONNX da internet na primeira execução - em rede fechada, informe um modelo local (ver README)."""
    nome = "chroma"

    def __init__(self, pasta: Path, embedding_function=None):
        import chromadb
        self.cli = chromadb.PersistentClient(path=str(pasta / "chroma"))
        kw = {"embedding_function": embedding_function} if embedding_function else {}
        self.col = self.cli.get_or_create_collection("aici", metadata={"hnsw:space": "cosine"}, **kw)
        self.arq = pasta / "chroma_manifesto.json"
        self.manifesto = json.loads(self.arq.read_text(encoding="utf8")) if self.arq.exists() else {}

    def remover_fonte(self, fonte: str):
        self.col.delete(where={"fonte": fonte})

    def adicionar(self, novos: list[Chunk]):
        for i in range(0, len(novos), 200):
            lote = novos[i:i + 200]
            self.col.add(ids=[c.id for c in lote], documents=[c.texto for c in lote],
                         metadatas=[{"tipo": c.tipo, "titulo": c.titulo, "fonte": c.fonte, "tema": c.tema, "ano": c.ano,
                                     "numero": c.numero, "origem": c.origem, "extra": json.dumps(c.extra)} for c in lote])

    def salvar(self):
        self.arq.write_text(json.dumps(self.manifesto), encoding="utf8")

    def limpar(self):
        self.cli.delete_collection("aici"); self.col = self.cli.get_or_create_collection("aici"); self.manifesto = {}

    def contagem(self) -> dict:
        return {"total": self.col.count()}

    def buscar(self, consulta: str, tipo: str | None, n: int):
        r = self.col.query(query_texts=[consulta], n_results=n, where={"tipo": tipo} if tipo else None)
        out = []
        for id_, doc, md, dist in zip(r["ids"][0], r["documents"][0], r["metadatas"][0], r["distances"][0]):
            c = Chunk(id=id_, tipo=md["tipo"], titulo=md["titulo"], fonte=md["fonte"], texto=doc, tema=md["tema"],
                      ano=md["ano"], numero=md["numero"], origem=md["origem"], extra=json.loads(md.get("extra", "{}")))
            out.append((c, 1.0 - float(dist), []))
        return out


def criar_store(settings, embedding_function=None):
    pasta = settings.caminho("vectorstore")
    if settings.get("indexador.backend", "lexical") == "chroma":
        return ChromaStore(pasta, embedding_function)
    return LexicalStore(pasta)


# ---------------------------------------------------------------- indexação
def indexar(settings, store=None, completo: bool = False, embedder=None) -> dict:
    """Indexa knowledge/. Incremental: só reprocessa arquivos novos ou alterados (hash). Remove os que sumiram."""
    store = store or criar_store(settings)
    raiz = settings.caminho("knowledge")
    exts = {e.lower() for e in settings.get("indexador.extensoes", [".pdf", ".docx", ".txt", ".md", ".json"])}
    tam, sobre = settings.get("indexador.chunk_chars", 1200), settings.get("indexador.chunk_sobreposicao", 150)
    if completo:
        store.limpar()
    vistos, novos, alterados, erros = set(), 0, 0, []
    for tipo in TIPOS:
        for arq in sorted((raiz / tipo).rglob("*")):
            if not arq.is_file() or arq.suffix.lower() not in exts or arq.name.startswith((".", "~$")):
                continue
            rel = arq.relative_to(raiz).as_posix()
            vistos.add(rel)
            h = _hash(arq)
            if store.manifesto.get(rel) == h:
                continue
            try:
                chunks = chunks_do_arquivo(raiz, arq, tam, sobre)
            except Exception as e:  # um arquivo corrompido não pode derrubar a indexação inteira
                erros.append(f"{rel}: {e}")
                continue
            if rel in store.manifesto:
                store.remover_fonte(rel); alterados += 1
            else:
                novos += 1
            store.adicionar(chunks)
            store.manifesto[rel] = h
    removidos = [r for r in list(store.manifesto) if r not in vistos]
    for r in removidos:
        store.remover_fonte(r); del store.manifesto[r]
    store.salvar()
    vetores = None
    if embedder is not None:
        if store.nome != "lexical":
            erros.append("embeddings híbridos só se combinam ao backend lexical (o Chroma já é vetorial)")
        else:
            from .embeddings import DenseStore
            vetores = DenseStore(settings.caminho("vectorstore")).sincronizar(store.chunks, embedder)
    return {"backend": store.nome, "novos": novos, "alterados": alterados, "removidos": len(removidos),
            "erros": erros, "chunks": store.contagem(), "vetores": vetores}
