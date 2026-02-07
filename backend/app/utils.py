# app/utils.py
import os
from werkzeug.utils import secure_filename


def caminho_seguro(base_dir, *componentes):
    """Garante que o caminho resultante não ultrapasse a raiz da base_dir."""
    caminho = os.path.abspath(os.path.join(base_dir, *componentes))
    if not caminho.startswith(os.path.abspath(base_dir)):
        raise PermissionError("Acesso negado ao caminho especificado.")
    return caminho


def nome_arquivo_pdf(nome):
    """Gera um nome de arquivo PDF seguro a partir do nome informado."""
    return secure_filename(f"{nome}.pdf")


def nome_arquivo_imagem_padrao():
    """Nome padrão seguro para uma imagem de capa."""
    return secure_filename("capa.jpg")
