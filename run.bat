@echo off
cd /d %~dp0
echo Iniciando FastAPI con Uvicorn...
call venv\Scripts\activate
uvicorn app.main:app --reload
pause
