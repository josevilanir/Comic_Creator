"""
Configuração do Gunicorn para produção.

Uso:
    gunicorn "main:app" --config gunicorn.conf.py

Variáveis de ambiente disponíveis:
    GUNICORN_BIND       Endereço de escuta         (padrão: 0.0.0.0:5000)
    GUNICORN_WORKERS    Número de worker processes  (padrão: 2 * CPUs + 1)
    GUNICORN_TIMEOUT    Timeout por request em s    (padrão: 120)
    GUNICORN_LOG_LEVEL  Nível de log               (padrão: info)
"""
import multiprocessing
import os

# ── Binding ───────────────────────────────────────────────────────────────────
bind = os.environ.get("GUNICORN_BIND", "0.0.0.0:5000")

# ── Workers ───────────────────────────────────────────────────────────────────
# Jobs de download são persistidos no SQLite, então múltiplos workers são
# seguros: qualquer worker pode ler/atualizar o estado do job via banco.
workers = int(os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"

# ── Timeouts ──────────────────────────────────────────────────────────────────
# 120 s para acomodar downloads de capítulo único que rodam de forma síncrona.
# Downloads em lote (range) retornam 202 imediatamente — sem problema de timeout.
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "120"))
graceful_timeout = 30
keepalive = 5

# ── Logging ───────────────────────────────────────────────────────────────────
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")
accesslog = "-"   # stdout
errorlog = "-"    # stderr
access_log_format = '%(h)s "%(r)s" %(s)s %(b)s %(D)sµs'
