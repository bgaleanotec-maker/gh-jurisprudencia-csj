@echo off
echo =====================================================
echo   GALEANO HERRERA ^| Jurisprudencia CSJ
echo =====================================================
echo.

cd /d "%~dp0"

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado. Instala Python 3.10+
    pause
    exit /b 1
)

REM Instalar dependencias si es la primera vez
if not exist ".deps_ok" (
    echo Instalando dependencias...
    pip install fastapi uvicorn pymupdf python-docx faiss-cpu google-generativeai python-multipart --break-system-packages -q
    echo. > .deps_ok
    echo Dependencias instaladas.
    echo.
)

REM Iniciar la app
echo Iniciando app en http://localhost:8000
echo Presiona Ctrl+C para detener.
echo.
start "" http://localhost:8000
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
