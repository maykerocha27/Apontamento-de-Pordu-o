@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Iniciando servidor do Apontamento de Producao...
start "" "http://localhost:8766"
py servidor_apontamento.py
pause
