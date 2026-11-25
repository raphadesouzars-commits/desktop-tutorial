#!/usr/bin/env python3
"""Exporta do gerador HTML (parecer/modelos/*.json) as categorias de atividade usadas pelo classificador
e copia os modelos completos para knowledge/modelos/atividades/.
O HTML continua sendo a fonte das categorias: rode este script sempre que um modelo for criado ou alterado."""
import json, pathlib, shutil

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ORIGEM = RAIZ.parent / "parecer" / "modelos"
DEST = RAIZ / "knowledge" / "modelos" / "atividades"


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    cats = []
    for f in sorted(ORIGEM.glob("*.json")):
        m = json.loads(f.read_text(encoding="utf8"))
        shutil.copyfile(f, DEST / f.name)
        cats.append({
            "id": m["id"], "nome": m["nome"], "grupo": m.get("grupo", ""), "descricao": m.get("descricao", ""),
            "palavrasChave": m.get("palavrasChave", []),
            "variantes": [{"id": v["id"], "rotulo": v["rotulo"], "resultado": v["resultado"], "fonte": v.get("fonte", ""),
                           "quandoUsar": v.get("quandoUsar", "")} for v in m["variantes"]],
        })
    (RAIZ / "config" / "categorias.json").write_text(json.dumps({"categorias": cats}, ensure_ascii=False, indent=1), encoding="utf8")
    print(f"{len(cats)} categorias exportadas")


if __name__ == "__main__":
    main()
