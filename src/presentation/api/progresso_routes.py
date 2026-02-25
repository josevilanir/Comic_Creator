"""
Endpoints de Progresso de Leitura — Isolados por usuário
"""
from flask import Blueprint, request, current_app, g
from src.presentation.api.jsend import success, fail, error
from src.presentation.decorators.auth_required import auth_required

progresso_bp = Blueprint("progresso", __name__, url_prefix="/api/v1/progresso")


@progresso_bp.route("/<path:manga>/<path:filename>", methods=["GET"])
@auth_required
def get_progresso(manga, filename):
    if '..' in manga or '..' in filename:
        return fail({"path": "Acesso negado"}, 403)

    try:
        container = current_app.container
        pagina = container.user_data_repository.get_progress(g.user_id, manga, filename)
        return success({"pagina": pagina})
    except Exception as e:
        return error(str(e), "GET_PROGRESSO_ERROR")


@progresso_bp.route("", methods=["POST"])
@auth_required
def save_progresso():
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
        container = current_app.container
        container.user_data_repository.save_progress(g.user_id, manga, filename, pagina)
        return success({"saved": True})
    except Exception as e:
        return error(str(e), "SAVE_PROGRESSO_ERROR")
