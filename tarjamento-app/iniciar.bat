@echo off
chcp 65001 >nul
title Tarjamento Coger — Corregedoria RFB

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║   Tarjamento Coger — Corregedoria da Receita Federal     ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo Iniciando servidor local...
echo.

:: Verificar se as bibliotecas foram baixadas
if not exist "assets\js\pdf.min.js" (
  echo ATENÇÃO: Bibliotecas não encontradas!
  echo Execute primeiro o script download-libs.bat para baixar as dependências.
  echo.
  pause
  exit /b 1
)

:: Tentar Python 3 primeiro
python --version >nul 2>&1
if %errorlevel% == 0 (
  echo Usando Python para servidor local na porta 8765...
  echo Acesse: http://localhost:8765
  echo Pressione Ctrl+C para encerrar.
  echo.
  start "" http://localhost:8765
  python -m http.server 8765
  goto :fim
)

:: Tentar Python 2
python2 --version >nul 2>&1
if %errorlevel% == 0 (
  echo Usando Python 2 para servidor local na porta 8765...
  start "" http://localhost:8765
  python2 -m SimpleHTTPServer 8765
  goto :fim
)

:: Tentar Node.js
node --version >nul 2>&1
if %errorlevel% == 0 (
  echo Usando Node.js para servidor local na porta 8765...
  start "" http://localhost:8765
  npx serve -l 8765 .
  goto :fim
)

echo ERRO: Nenhum servidor HTTP disponível.
echo Instale Python 3 (https://python.org) ou Node.js (https://nodejs.org)
echo e execute este script novamente.
echo.
pause

:fim
