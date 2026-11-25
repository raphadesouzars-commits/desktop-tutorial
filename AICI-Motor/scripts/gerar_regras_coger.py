#!/usr/bin/env python3
"""Gera knowledge/regras_coger.md a partir dos DADOS do projeto (categorias do HTML, templates institucionais), para que o
documento nunca divirja do que o gerador faz. A seção "A consolidar" é preenchida pela COGER e preservada nas próximas gerações."""
import json, pathlib, re

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "knowledge" / "regras_coger.md"
MARCA = "## 7. A consolidar pela COGER"
PADRAO_A_CONSOLIDAR = f"""{MARCA}

(Esta seção é editada à mão e preservada quando o arquivo é regenerado. Registre aqui os princípios consolidados da COGER que
ainda não constam de nenhum normativo ou parecer, cada um com a data e a origem, por exemplo: "Magistério: sempre exigir
compatibilidade de horários - PA 145/2025".)

- [pendente]
"""


def main():
    cats = json.loads((RAIZ / "config" / "categorias.json").read_text(encoding="utf8"))["categorias"]
    inst = json.loads((RAIZ / "templates" / "institucional.json").read_text(encoding="utf8"))
    grupos: dict[str, list[str]] = {}
    for c in cats:
        grupos.setdefault(c.get("grupo") or "Outras situações", []).append(c["nome"])
    manual = PADRAO_A_CONSOLIDAR
    if SAIDA.exists() and MARCA in (antigo := SAIDA.read_text(encoding="utf8")):
        manual = antigo[antigo.index(MARCA):]
    L = ["# Regras institucionais da COGER para pareceres de conflito de interesses", "",
         "Documento de apoio às análises (consulte antes de sugerir fundamentações). Gerado de `config/categorias.json` e "
         "`templates/institucional.json`; os modelos e os pareceres da biblioteca prevalecem em caso de divergência.", "",
         "## 1. Papel da IA e do parecerista", "",
         "- A decisão final pertence ao parecerista; a IA é consultiva e toda sugestão deve ser validada.",
         "- Documentos institucionais têm prioridade sobre conhecimento externo; precedentes da COGER pesam mais que os demais.",
         "- Nenhum documento é alterado automaticamente pela IA. Nunca inventar fundamento: citar sempre a origem.", "",
         "## 2. Resultados possíveis de um parecer", ""]
    L += [f"- **{k}**: {v}" for k, v in inst["rotulo_resultado"].items()]
    L += ["", "## 3. Categorias válidas de atividade", "",
          "A classificação deve escolher **somente** entre as categorias abaixo (agrupadas como no modelo do gerador):", ""]
    for g, nomes in sorted(grupos.items()):
        L.append(f"**{g}** ({len(nomes)}): " + "; ".join(sorted(nomes)) + ".")
        L.append("")
    L += ["## 4. Estrutura padrão do parecer", "",
          "I. RELATÓRIO (abertura, identificação do servidor e respostas do formulário SeCI, perguntas 1 a 10); "
          "II. FUNDAMENTOS (análise da atividade à luz da Lei nº 12.813/2013 e da Lei nº 8.112/1990, art. 117); III. CONCLUSÃO.", "",
          f"Órgão citado na conclusão: {inst['orgao']}. Norma procedimental: {inst['portaria_curta']}.", "",
          "## 5. Compromissos e ressalvas aceitos", "",
          "Em qualquer autorização, o servidor deve (item 13 do Parecer Coger/GNP nº 522/2023):", ""]
    L += [f"{chr(97 + i)}) {d}" for i, d in enumerate(inst["deveres"])]
    L += ["", "Regras de uso:", "",
          "- Autorização **com ressalvas** (risco mitigável) sempre vem acompanhada de **Termo de Compromisso**, assinado perante a Comissão de Ética e a chefia imediata.",
          f"- Fecho padrão: \"{inst['nova_consulta'].replace('{{g:pelo consulente|pela consulente}}', 'pelo consulente')}\"", "",
          "## 6. Encaminhamento", "",
          f"- Sem conflito: \"{inst['encaminha']}\"",
          "- Com conflito: encaminhar à Comissão de Ética para prosseguimento e remessa à Controladoria-Geral da União pelo SeCI (Portaria Interministerial nº 333/2013).", "",
          manual.rstrip() + ""]
    SAIDA.write_text("\n".join(L), encoding="utf8")
    print(f"{SAIDA} ({SAIDA.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
