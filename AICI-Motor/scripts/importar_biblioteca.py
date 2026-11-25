#!/usr/bin/env python3
"""Copia a biblioteca (pasta exportada/sincronizada do SharePoint ou Drive) para knowledge/, na estrutura que o motor lê:
   01_Pareceres_Emitidos -> knowledge/pareceres      02_Precedentes -> knowledge/precedentes
   03_Normativos         -> knowledge/normativos     04_Modelos_Institucionais -> knowledge/modelos
Uso: python scripts/importar_biblioteca.py <pasta_da_biblioteca> [--sincronizar]
Com --sincronizar, apaga de knowledge/ o que já não existe na origem. Depois, reindexe (POST /indexar ou reinicie o motor)."""
import argparse, pathlib, shutil

RAIZ = pathlib.Path(__file__).resolve().parent.parent
MAPA = {"01_Pareceres_Emitidos": "pareceres", "02_Precedentes": "precedentes", "03_Normativos": "normativos", "04_Modelos_Institucionais": "modelos"}
EXT = {".pdf", ".docx", ".txt", ".md", ".json"}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("origem"); ap.add_argument("--sincronizar", action="store_true")
    a = ap.parse_args()
    origem = pathlib.Path(a.origem)
    for pasta, destino in MAPA.items():
        src, dst = origem / pasta, RAIZ / "knowledge" / destino
        if not src.is_dir():
            print(f"[aviso] {pasta} não encontrada em {origem}"); continue
        copiados, vistos = 0, set()
        for f in src.rglob("*"):
            if not f.is_file() or f.suffix.lower() not in EXT or f.name.startswith(("~$", ".")):
                continue
            rel = f.relative_to(src)
            if "_Duplicados_Revisar" in rel.parts:      # duplicados aguardam revisão humana: fora da base
                continue
            vistos.add(rel)
            alvo = dst / rel
            if not alvo.exists() or alvo.stat().st_mtime < f.stat().st_mtime or alvo.stat().st_size != f.stat().st_size:
                alvo.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(f, alvo); copiados += 1
        removidos = 0
        if a.sincronizar and dst.is_dir():
            for f in dst.rglob("*"):
                if f.is_file() and f.name != ".gitkeep" and f.relative_to(dst) not in vistos and not (destino == "modelos" and "atividades" in f.parts):
                    f.unlink(); removidos += 1
        print(f"{pasta}: {copiados} copiado(s), {removidos} removido(s)")


if __name__ == "__main__":
    main()
