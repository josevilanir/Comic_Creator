# Comic Creator — comandos de desenvolvimento
# Uso: make <target>

.PHONY: help dev-backend dev-frontend install test test-unit test-integration test-cov lint

help: ## Mostra esta ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Setup ────────────────────────────────────────────────────────────────────

install: ## Instala dependências do backend e frontend
	pip install -r requirements.txt
	cd frontend && npm install

# ── Dev servers ──────────────────────────────────────────────────────────────

dev-backend: ## Inicia o servidor Flask (porta 5000)
	python main.py

dev-frontend: ## Inicia o servidor Vite (porta 5173)
	cd frontend && npm run dev

# ── Tests ────────────────────────────────────────────────────────────────────

test: ## Executa todos os testes
	pytest Tests/ -v

test-unit: ## Executa apenas testes unitários
	pytest Tests/unit/ -v -m unit

test-integration: ## Executa apenas testes de integração
	pytest Tests/integration/ -v -m integration

test-cov: ## Executa todos os testes com cobertura (HTML + terminal)
	pytest Tests/ -v --cov=src --cov-report=html --cov-report=term
	@echo "Relatório de cobertura disponível em: htmlcov/index.html"

# ── Production ───────────────────────────────────────────────────────────────

start: ## Inicia o servidor Gunicorn (produção)
	gunicorn "main:app" --config deploy/gunicorn.conf.py
