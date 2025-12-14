#!/bin/bash

# BookLayout - Script de Inicialização

echo "🚀 Iniciando BookLayout..."
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar Python
echo "📦 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 não encontrado. Por favor, instale Python 3.8+${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python encontrado$(python3 --version)${NC}"

# Criar ambiente virtual (opcional)
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Ambiente virtual criado${NC}"
fi

# Ativar ambiente virtual
echo ""
echo "📦 Ativando ambiente virtual..."
source venv/bin/activate
echo -e "${GREEN}✓ Ambiente virtual ativado${NC}"

# Instalar dependências
echo ""
echo "📦 Instalando dependências..."
cd backend
pip install -r requirements.txt > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependências instaladas${NC}"
else
    echo -e "${RED}❌ Erro ao instalar dependências${NC}"
    exit 1
fi
cd ..

# Iniciar servidor
echo ""
echo -e "${YELLOW}🌐 Iniciando servidor...${NC}"
echo ""
echo "📚 BookLayout está pronto!"
echo ""
echo -e "${GREEN}Backend:${NC}  http://localhost:5000"
echo -e "${GREEN}Frontend:${NC} http://localhost:8000"
echo ""
echo "Para abrir o frontend, execute em outro terminal:"
echo "  cd frontend && python -m http.server 8000"
echo ""
echo "Pressione Ctrl+C para parar o servidor"
echo ""

cd backend
python app.py