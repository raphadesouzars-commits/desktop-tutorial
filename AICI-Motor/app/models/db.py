"""Banco operacional (SQLite). Tabelas: consultas, pareceres, metricas. Para PostgreSQL, troque apenas esta camada."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path

DDL = """
CREATE TABLE IF NOT EXISTS consultas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  data TEXT NOT NULL DEFAULT (datetime('now')),
  arquivo TEXT NOT NULL,
  usuario TEXT DEFAULT '',
  atividade TEXT DEFAULT '',
  resultado TEXT DEFAULT '',
  status TEXT NOT NULL DEFAULT 'recebida'
);
CREATE TABLE IF NOT EXISTS pareceres (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  consulta_id INTEGER NOT NULL REFERENCES consultas(id),
  resultado TEXT DEFAULT '',
  modelo TEXT DEFAULT '',
  arquivo_saida TEXT DEFAULT '',
  data TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS metricas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  data TEXT NOT NULL DEFAULT (date('now')),
  atividade TEXT DEFAULT '',
  resultado TEXT DEFAULT '',
  precedente_utilizado TEXT DEFAULT ''
);
"""


class Banco:
    def __init__(self, caminho: Path):
        self.caminho = Path(caminho)
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        with self.conexao() as c:
            c.executescript(DDL)

    @contextmanager
    def conexao(self):
        c = sqlite3.connect(self.caminho)
        c.row_factory = sqlite3.Row
        try:
            yield c
            c.commit()
        finally:
            c.close()

    def inserir(self, tabela: str, **campos) -> int:
        cols = ", ".join(campos)
        ph = ", ".join("?" for _ in campos)
        with self.conexao() as c:
            return c.execute(f"INSERT INTO {tabela} ({cols}) VALUES ({ph})", tuple(campos.values())).lastrowid

    def atualizar(self, tabela: str, id_: int, **campos) -> None:
        sets = ", ".join(f"{k}=?" for k in campos)
        with self.conexao() as c:
            c.execute(f"UPDATE {tabela} SET {sets} WHERE id=?", (*campos.values(), id_))

    def obter(self, tabela: str, id_: int) -> dict | None:
        with self.conexao() as c:
            r = c.execute(f"SELECT * FROM {tabela} WHERE id=?", (id_,)).fetchone()
            return dict(r) if r else None

    def consultar(self, sql: str, params: tuple = ()) -> list[dict]:
        with self.conexao() as c:
            return [dict(r) for r in c.execute(sql, params).fetchall()]
