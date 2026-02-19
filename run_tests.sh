#!/bin/bash

# Script de execução de testes para Comic Creator
# Use: chmod +x run_tests.sh && ./run_tests.sh

echo "🧪 Executando testes do Comic Creator..."

# Testes unitários
echo "📋 Testes Unitários:"
pytest tests/unit/ -v -m unit

if [ $? -eq 0 ]; then
    echo "✅ Testes unitários passaram"
else
    echo "❌ Testes unitários falharam"
fi

# Testes de integração
echo ""
echo "🔗 Testes de Integração:"
pytest tests/integration/ -v -m integration

if [ $? -eq 0 ]; then
    echo "✅ Testes de integração passaram"
else
    echo "❌ Testes de integração falharam"
fi

# Todos os testes com cobertura
echo ""
echo "📊 Executando todos os testes com cobertura:"
pytest tests/ -v --cov=src --cov-report=html --cov-report=term

echo ""
echo "✅ Testes concluídos!"
echo "📄 Relatório de cobertura disponível em: htmlcov/index.html"
