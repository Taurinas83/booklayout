@echo off
REM BookLayout - Script de Inicialização para Windows

echo.
echo 🚀 Iniciando BookLayout...
echo.

REM Verificar Python
echo 📦 Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado. Por favor, instale Python 3.8+
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✓ %PYTHON_VERSION% encontrado

REM Criar ambiente virtual
if not exist "venv" (
    echo.
    echo 📦 Criando ambiente virtual...
    python -m venv venv
    echo ✓ Ambiente virtual criado
)

REM Ativar ambiente virtual
echo.
echo 📦 Ativando ambiente virtual...
call venv\Scripts\activate.bat
echo ✓ Ambiente virtual ativado

REM Instalar dependências
echo.
echo 📦 Instalando dependências...
cd backend
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ❌ Erro ao instalar dependências
    pause
    exit /b 1
)
echo ✓ Dependências instaladas
cd ..

REM Iniciar servidor
echo.
echo 🌐 Iniciando servidor...
echo.
echo 📚 BookLayout está pronto!
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:8000
echo.
echo Para abrir o frontend, execute em outro terminal:
echo   cd frontend ^&^& python -m http.server 8000
echo.
echo Pressione Ctrl+C para parar o servidor
echo.

cd backend
python app.py
pause