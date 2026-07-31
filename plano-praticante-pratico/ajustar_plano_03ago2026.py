# -*- coding: utf-8 -*-
"""
Ajusta o Plano de Estudos (Praticante de Prático) para iniciar em 03/08/2026.

O arquivo de entrada já está na estrutura final de 60 semanas (Fase 1: 1-26,
Fase 2 com fechamento condensado: 27-52, Fase 3: 53-60), mas com Semana 1
começando em 06/Jul/2026. Este script apenas desloca todas as datas em
+28 dias (4 semanas) para que a Semana 1 passe a começar em 03/Ago/2026,
e atualiza os textos globais (barra lateral, dashboard) e o array PHASES.

Diferente do script "ajustar_plano_datas.py" (que parte do arquivo original
de 56 semanas, começando em 11/Mai/2026, e faz a condensação da Fase 2 +
inserção da Fase 3), este script NÃO deve repetir a condensação/inserção,
pois o arquivo de entrada já as contém.

USO:
    python3 ajustar_plano_03ago2026.py /caminho/para/Plano_de_Estudos_Standalone.html
"""
import re
import sys
import shutil
import datetime as dt

MESES = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
         7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'}
MESES_INV = {v: k for k, v in MESES.items()}

SHIFT = dt.timedelta(days=28)


def fmt_period(d_ini, d_fim, n):
    if d_ini.month == d_fim.month:
        s = f"{d_ini.day:02d}–{d_fim.day:02d}/{MESES[d_fim.month]}/{d_fim.year}"
    elif d_ini.year == d_fim.year:
        s = f"{d_ini.day:02d}/{MESES[d_ini.month]}–{d_fim.day:02d}/{MESES[d_fim.month]}/{d_fim.year}"
    else:
        s = f"{d_ini.day:02d}/{MESES[d_ini.month]}/{d_ini.year}–{d_fim.day:02d}/{MESES[d_fim.month]}/{d_fim.year}"
    return f"{s} · Semana {n}"


def parse_period(s):
    m = re.match(r"(\d{2})(?:/([A-Za-z]{3})(?:/(\d{4}))?)?[–-](\d{2})/([A-Za-z]{3})/(\d{4})", s)
    if not m:
        raise ValueError(f"Não foi possível interpretar o período: {s!r}")
    d1, mon1, year1_explicit, d2, mon2, year2 = m.groups()
    year2 = int(year2)
    mon2_n = MESES_INV[mon2]
    mon1_n = MESES_INV[mon1] if mon1 else mon2_n
    year1 = int(year1_explicit) if year1_explicit else (year2 if mon1_n <= mon2_n else year2 - 1)
    return dt.date(year1, mon1_n, int(d1)), dt.date(year2, mon2_n, int(d2))


def shift_phase_period(period_str):
    """Shifts strings like '06 Jul 2026 – 03 Jan 2027' or
    '05 Jul – 29 Ago 2027 (8 semanas)' by SHIFT days."""
    m = re.match(
        r"(\d{2}) ([A-Za-z]{3})(?: (\d{4}))? [–-] (\d{2}) ([A-Za-z]{3}) (\d{4})(.*)$",
        period_str)
    if not m:
        raise ValueError(f"Não foi possível interpretar período de fase: {period_str!r}")
    d1, mon1, year1_explicit, d2, mon2, year2, suffix = m.groups()
    year2 = int(year2)
    mon2_n = MESES_INV[mon2]
    mon1_n = MESES_INV[mon1]
    year1 = int(year1_explicit) if year1_explicit else (year2 if mon1_n <= mon2_n else year2 - 1)
    d_ini = dt.date(year1, mon1_n, int(d1)) + SHIFT
    d_fim = dt.date(year2, mon2_n, int(d2)) + SHIFT
    if d_ini.year == d_fim.year:
        return f"{d_ini.day:02d} {MESES[d_ini.month]} – {d_fim.day:02d} {MESES[d_fim.month]} {d_fim.year}{suffix}"
    return f"{d_ini.day:02d} {MESES[d_ini.month]} {d_ini.year} – {d_fim.day:02d} {MESES[d_fim.month]} {d_fim.year}{suffix}"


def main(path):
    backup = path + ".bak"
    shutil.copy(path, backup)
    print(f"Backup criado em: {backup}")

    with open(path, encoding="utf-8") as f:
        content = f.read()

    # 1) Deslocar as datas de TODAS as semanas (1 a 60) em +28 dias
    pattern = re.compile(r"'(w(\d+))',(\d+),(\d+),\s*('[^']*'),\s*'([^']*Semana \d+)'")
    count = 0

    def repl(m):
        nonlocal count
        wid, _n_in_id, ph, n, title, period = m.groups()
        n = int(n)
        d_ini, d_fim = parse_period(period)
        new_ini, new_fim = d_ini + SHIFT, d_fim + SHIFT
        count += 1
        return f"'{wid}',{ph},{n},{title},'{fmt_period(new_ini, new_fim, n)}'"

    content = pattern.sub(repl, content)
    print(f"Datas deslocadas em +28 dias para {count} semanas (esperado: 60).")
    if count != 60:
        print("ATENÇÃO: número de semanas deslocadas diferente de 60 — revisar antes de prosseguir.")

    # 2) Textos globais fixos
    content = content.replace(
        '<div class="sb-meta-val">06 Jul 26</div>',
        '<div class="sb-meta-val">03 Ago 26</div>'
    )
    content = content.replace(
        'Início em 06 de julho de 2026',
        'Início em 03 de agosto de 2026'
    )

    # 3) Array PHASES
    for old_period in [
        "06 Jul 2026 – 03 Jan 2027",
        "04 Jan – 04 Jul 2027",
        "05 Jul – 29 Ago 2027 (8 semanas)",
    ]:
        new_period = shift_phase_period(old_period)
        marker = f"period:'{old_period}'"
        if marker not in content:
            raise RuntimeError(f"Período de fase não encontrado: {old_period!r}")
        content = content.replace(marker, f"period:'{new_period}'")
        print(f"PHASES period atualizado: {old_period!r} -> {new_period!r}")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print("Arquivo atualizado com sucesso:", path)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 ajustar_plano_03ago2026.py /caminho/para/Plano_de_Estudos_Standalone.html")
        sys.exit(1)
    main(sys.argv[1])
