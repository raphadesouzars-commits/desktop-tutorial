#!/usr/bin/env bash
# Monta veritas_digital_coger.html a partir de coger-ui.css + src/app.css + src/app.js + src/template.html
set -euo pipefail
cd "$(dirname "$0")"

python3 - <<'EOF'
with open('src/template.html', 'r', encoding='utf-8') as f:
    template = f.read()
with open('coger-ui.css', 'r', encoding='utf-8') as f:
    coger_css = f.read()
with open('src/app.css', 'r', encoding='utf-8') as f:
    app_css = f.read()
with open('src/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

out = template.replace('/*__COGER_UI_CSS__*/', coger_css)
out = out.replace('/*__APP_CSS__*/', app_css)
out = out.replace('/*__APP_JS__*/', app_js)

with open('veritas_digital_coger.html', 'w', encoding='utf-8') as f:
    f.write(out)

print("veritas_digital_coger.html gerado:", len(out), "bytes")
EOF
