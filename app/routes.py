# app/routes.py
import os
from flask import Blueprint, request, render_template, send_file, redirect, url_for, flash, abort, current_app
from werkzeug.utils import secure_filename
from .downloader import baixar_capitulo_para_pdf, extrair_nome_manga
from .utils import caminho_seguro, nome_arquivo_pdf, nome_arquivo_imagem_padrao

bp = Blueprint("routes", __name__)


@bp.route("/")
def index():
    base_dir = current_app.config["BASE_DIR"]
    mangas = sorted(os.listdir(base_dir))
    return render_template("index.html", mangas=mangas)


@bp.route("/baixar", methods=["POST"])
def baixar():
    base_dir = current_app.config["BASE_DIR"]
    url = request.form.get("url")
    if not url:
        flash("URL inválida.", "error")
        return redirect(url_for("routes.index"))

    nome_manga = extrair_nome_manga(url)
    pasta_manga = os.path.join(base_dir, nome_manga)
    os.makedirs(pasta_manga, exist_ok=True)

    capitulo = request.form.get("capitulo") or "capitulo"
    nome_pdf = nome_arquivo_pdf(capitulo)
    caminho_pdf = os.path.join(pasta_manga, nome_pdf)

    sucesso, mensagem = baixar_capitulo_para_pdf(url, caminho_pdf)
    flash(mensagem, "success" if sucesso else "error")
    return redirect(url_for("routes.index"))


@bp.route("/ler/<manga>/<arquivo>")
def ler(manga, arquivo):
    try:
        caminho = caminho_seguro(current_app.config["BASE_DIR"], manga, arquivo)
    except PermissionError:
        abort(403)
    return send_file(caminho)


@bp.route("/excluir/<manga>/<arquivo>", methods=["POST"])
def excluir(manga, arquivo):
    try:
        caminho = caminho_seguro(current_app.config["BASE_DIR"], manga, arquivo)
        os.remove(caminho)
        flash(f"Capítulo '{arquivo}' excluído.", "success")
    except (PermissionError, FileNotFoundError):
        flash("Erro ao excluir capítulo.", "error")
    return redirect(url_for("routes.index"))


@bp.route("/enviar_capa/<manga>", methods=["POST"])
def enviar_capa(manga):
    capa = request.files.get("capa")
    if not capa:
        flash("Nenhuma imagem enviada.", "error")
        return redirect(url_for("routes.index"))

    nome = nome_arquivo_imagem_padrao()
    try:
        caminho = caminho_seguro(current_app.config["BASE_DIR"], manga, nome)
        capa.save(caminho)
        flash("Capa enviada com sucesso.", "success")
    except PermissionError:
        flash("Acesso negado ao enviar capa.", "error")
    return redirect(url_for("routes.index"))
