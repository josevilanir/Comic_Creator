# ── Build stage ───────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Dependências de sistema necessárias para Pillow e PyMuPDF
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Runtime stage ─────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Dependências de runtime para Pillow e PyMuPDF
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copia pacotes instalados do builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copia código da aplicação
COPY . .

# Cria diretórios necessários (volume será montado em /data e /comics)
RUN mkdir -p /data /comics /app/logs

# Variáveis de ambiente padrão
ENV FLASK_ENV=production \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

EXPOSE 8080

# Inicia com Gunicorn
CMD gunicorn "main:app" --config gunicorn.conf.py