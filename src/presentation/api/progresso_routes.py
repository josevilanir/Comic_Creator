"""
Endpoints de Progresso de Leitura
"""
from flask import Blueprint, request, current_app
from src.presentation.api.jsend import success, fail, error

progresso_bp = Blueprint("progresso", __name__, url_prefix="/api/v1/progresso")


def _get_repo():
    """Helper: instancia o ProgressoRepository com o caminho correto."""
    from src.infrastructure.persistence.progresso_repository import ProgressoRepository
    from config.settings import Config
    path = str(Config.DATA_DIR / 'progresso.json')
    return ProgressoRepository(path)


@progresso_bp.route("/<path:manga>/<path:filename>", methods=["GET"])
def get_progresso(manga, filename):
    """
    Retorna a última página salva para um capítulo.

    GET /api/v1/progresso/{manga}/{filename}
    Resposta: { "status": "success", "data": { "pagina": 7 } }
    """
    if '..' in manga or '..' in filename:
        return fail({"path": "Acesso negado"}, 403)

    try:
        repo = _get_repo()
        pagina = repo.get_pagina(manga, filename)
        return success({"pagina": pagina})
    except Exception as e:
        return error(str(e), "GET_PROGRESSO_ERROR")


@progresso_bp.route("", methods=["POST"])
def save_progresso():
    """
    Salva o progresso de leitura.

    POST /api/v1/progresso
    Body: { "manga": "NomeManga", "filename": "cap1.pdf", "pagina": 7 }
    Resposta: { "status": "success", "data": { "saved": true } }
    """
    data     = request.json or {}
    manga    = data.get("manga", "").strip()
    filename = data.get("filename", "").strip()
    pagina   = data.get("pagina")

    if not manga or not filename:
        return fail({"manga": "obrigatório", "filename": "obrigatório"})
    if pagina is None or not isinstance(pagina, int) or pagina < 1:
        return fail({"pagina": "obrigatório e deve ser inteiro >= 1"})
    if '..' in manga or '..' in filename:
        return fail({"path": "Acesso negado"}, 403)

    try:
        repo = _get_repo()
        repo.save_pagina(manga, filename, pagina)
        return success({"saved": True})
    except Exception as e:
        return error(str(e), "SAVE_PROGRESSO_ERROR")
