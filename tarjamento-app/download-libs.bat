@echo off
chcp 65001 >nul
title Download das Bibliotecas — Tarjamento Coger

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║   Download das Bibliotecas — Tarjamento Coger            ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo Este script baixa as bibliotecas necessárias para uso offline.
echo Apos a conclusao, a ferramenta nao precisara mais de internet.
echo.

:: Criar diretórios
if not exist "assets\js\tesseract" mkdir "assets\js\tesseract"
if not exist "assets\lang" mkdir "assets\lang"

:: Verificar se curl está disponível (Windows 10+)
curl --version >nul 2>&1
if %errorlevel% neq 0 (
  echo AVISO: curl nao encontrado. Tentando com PowerShell...
  set USE_POWERSHELL=1
)

set PDFJS_VERSION=4.9.155

echo [1/4] Baixando PDF.js...
if defined USE_POWERSHELL (
  powershell -Command "Invoke-WebRequest 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/%PDFJS_VERSION%/pdf.min.js' -OutFile 'assets\js\pdf.min.js'"
  powershell -Command "Invoke-WebRequest 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/%PDFJS_VERSION%/pdf.worker.min.js' -OutFile 'assets\js\pdf.worker.min.js'"
) else (
  curl -fsSL "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/%PDFJS_VERSION%/pdf.min.js" -o "assets\js\pdf.min.js"
  curl -fsSL "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/%PDFJS_VERSION%/pdf.worker.min.js" -o "assets\js\pdf.worker.min.js"
)
echo    OK - PDF.js instalado

echo [2/4] Baixando jsPDF...
if defined USE_POWERSHELL (
  powershell -Command "Invoke-WebRequest 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js' -OutFile 'assets\js\jspdf.min.js'"
) else (
  curl -fsSL "https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js" -o "assets\js\jspdf.min.js"
)
echo    OK - jsPDF instalado

echo [3/4] Baixando Tesseract.js...
if defined USE_POWERSHELL (
  powershell -Command "Invoke-WebRequest 'https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js' -OutFile 'assets\js\tesseract.min.js'"
  powershell -Command "Invoke-WebRequest 'https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/worker.min.js' -OutFile 'assets\js\tesseract\worker.min.js'"
  powershell -Command "Invoke-WebRequest 'https://cdn.jsdelivr.net/npm/tesseract.js-core@5/tesseract-core.wasm.js' -OutFile 'assets\js\tesseract\tesseract-core.wasm.js'"
) else (
  curl -fsSL "https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js" -o "assets\js\tesseract.min.js"
  curl -fsSL "https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/worker.min.js" -o "assets\js\tesseract\worker.min.js"
  curl -fsSL "https://cdn.jsdelivr.net/npm/tesseract.js-core@5/tesseract-core.wasm.js" -o "assets\js\tesseract\tesseract-core.wasm.js"
)
echo    OK - Tesseract.js instalado

echo [4/4] Baixando dados de idioma portugues (~10 MB)...
if defined USE_POWERSHELL (
  powershell -Command "Invoke-WebRequest 'https://github.com/naptha/tessdata/raw/gh-pages/4.0.0/por.traineddata.gz' -OutFile 'assets\lang\por.traineddata.gz'"
) else (
  curl -fsSL "https://github.com/naptha/tessdata/raw/gh-pages/4.0.0/por.traineddata.gz" -o "assets\lang\por.traineddata.gz"
)
echo    Descompactando...
powershell -Command "& { Add-Type -AssemblyName System.IO.Compression.FileSystem; $src='assets\lang\por.traineddata.gz'; $dst='assets\lang\por.traineddata'; $fs=[System.IO.File]::OpenRead($src); $gs=New-Object System.IO.Compression.GzipStream($fs,[System.IO.Compression.CompressionMode]::Decompress); $out=[System.IO.File]::Create($dst); $gs.CopyTo($out); $out.Close(); $gs.Close(); $fs.Close(); Remove-Item $src }"
echo    OK - Dados de idioma instalados

echo.
echo Download concluido! Execute iniciar.bat para abrir a ferramenta.
echo.
pause
