# Script de execução de testes para Comic Creator
# Use: .\run_tests.ps1

Write-Host "🧪 Executando testes do Comic Creator..." -ForegroundColor Cyan

# Cores para output
$green = "Green"
$blue = "Blue"
$yellow = "Yellow"

# Testes unitários
Write-Host "`n📋 Testes Unitários:" -ForegroundColor $blue
pytest tests/unit/ -v -m unit
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Testes unitários passaram" -ForegroundColor $green
} else {
    Write-Host "❌ Testes unitários falharam" -ForegroundColor Red
}

# Testes de integração
Write-Host "`n🔗 Testes de Integração:" -ForegroundColor $blue
pytest tests/integration/ -v -m integration
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Testes de integração passaram" -ForegroundColor $green
} else {
    Write-Host "❌ Testes de integração falharam" -ForegroundColor Red
}

# Todos os testes com cobertura
Write-Host "`n📊 Executando todos os testes com cobertura:" -ForegroundColor $blue
pytest tests/ -v --cov=src --cov-report=html --cov-report=term

Write-Host "`n✅ Testes concluídos!" -ForegroundColor $green
Write-Host "📄 Relatório de cobertura disponível em: htmlcov/index.html" -ForegroundColor $yellow
