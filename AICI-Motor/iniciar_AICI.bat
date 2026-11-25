@echo off
rem Inicia o motor AICI. Na primeira vez, instala as dependencias (precisa de Python 3.12+ e acesso ao repositorio de pacotes).
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Python nao encontrado. Instale o Python 3.12 ou superior ou peca a TI, e execute este arquivo de novo.
  pause
  exit /b 1
)
if not exist ".venv" python -m venv .venv
call ".venv\Scripts\activate.bat"
if not exist ".venv\instalado.txt" (
  pip install -r requirements.txt
  if errorlevel 1 (
    echo Falha ao instalar as dependencias. Verifique o acesso a internet/repositorio de pacotes com a TI.
    pause
    exit /b 1
  )
  echo ok> ".venv\instalado.txt"
)
echo.
echo Motor AICI em http://127.0.0.1:8765  (mantenha esta janela aberta; feche-a para desligar)
echo.
python main.py
pause
