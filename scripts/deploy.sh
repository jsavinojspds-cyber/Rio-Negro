#!/bin/bash
# Deploy manual do Rio Negro Dashboard
# (Normalmente desnecessário — o GitHub Actions faz isso automaticamente
#  de seg-sex às 8h. Use este script só para deploys manuais/emergenciais.)
#
# Uso: ./scripts/deploy.sh [mensagem de commit]

set -e

PROJECT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$PROJECT_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 Deploy manual — Rio Negro Dashboard${NC}"

# Copiar arquivos para a raiz (GitHub Pages serve a partir de /)
cp src/index.html index.html
cp src/data.js data.js
echo -e "${GREEN}✅ index.html e data.js copiados para a raiz${NC}"

if [ -z "$(git status --porcelain 2>/dev/null)" ]; then
    echo -e "${YELLOW}⚠️  Nenhuma mudança para fazer deploy${NC}"
    exit 0
fi

COMMIT_MSG="${1:-Update manual: $(date +'%Y-%m-%d %H:%M')}"

git add .
git commit -m "$COMMIT_MSG"
git push origin main

echo ""
echo -e "${GREEN}🎉 Deploy concluído!${NC}"
echo "🌐 App atualizado em 1-2 minutos:"
echo "   https://jsavinojspds-cyber.github.io/rio-negro"
