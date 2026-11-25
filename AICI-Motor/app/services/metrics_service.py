"""Módulo 12 - Indicadores. Todo parecer gerado registra: atividade, resultado, precedente utilizado e data."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path


class Metricas:
    def __init__(self, banco, pasta: Path):
        self.db, self.pasta = banco, Path(pasta)

    def registrar(self, atividade: str, resultado: str, precedente: str, data: str | None = None) -> dict:
        data = data or date.today().isoformat()
        self.db.inserir("metricas", data=data, atividade=atividade, resultado=resultado, precedente_utilizado=precedente)
        reg = {"atividade": atividade, "resultado": resultado, "precedente": precedente, "data": data}
        self.pasta.mkdir(parents=True, exist_ok=True)
        with (self.pasta / "metricas.jsonl").open("a", encoding="utf8") as f:   # trilha de auditoria (RNF004)
            f.write(json.dumps(reg, ensure_ascii=False) + "\n")
        return reg

    def indicadores(self) -> dict:
        q = self.db.consultar
        return {
            "total_consultas": q("SELECT COUNT(*) n FROM consultas")[0]["n"],
            "total_pareceres": q("SELECT COUNT(*) n FROM pareceres")[0]["n"],
            "por_atividade": q("SELECT atividade, COUNT(*) n FROM metricas GROUP BY atividade ORDER BY n DESC"),
            "por_resultado": q("SELECT resultado, COUNT(*) n FROM metricas GROUP BY resultado ORDER BY n DESC"),
            "precedentes_mais_utilizados": q("SELECT precedente_utilizado precedente, COUNT(*) n FROM metricas "
                                              "WHERE precedente_utilizado<>'' GROUP BY precedente_utilizado ORDER BY n DESC LIMIT 10"),
            "por_mes": q("SELECT substr(data,1,7) mes, COUNT(*) n FROM metricas GROUP BY mes ORDER BY mes"),
        }
