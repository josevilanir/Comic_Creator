import json
import os
import re
from urllib.parse import urlparse
from flask import current_app


def carregar_urls():
    path = current_app.config['URLS_JSON']
    if os.path.exists(path):
        with open(path, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                current_app.logger.error(f'Erro ao decodificar {path}.')
                return {}
    return {}


def salvar_urls(urls):
    path = current_app.config['URLS_JSON']
    with open(path, 'w') as f:
        json.dump(urls, f, indent=4)


def limpar_sufixo_manga_pt_br(nome_manga_str):
    if not nome_manga_str or nome_manga_str == 'Manga Desconhecido':
        return nome_manga_str

    patterns_to_remove = [
        r"[ _\-]manga[ _\-]pt[ _\-]br$",
        r"[ _\-]pt[ _\-]br$",
    ]
    cleaned_name = nome_manga_str
    for pattern in patterns_to_remove:
        new_name, num_subs = re.subn(pattern, '', cleaned_name, flags=re.IGNORECASE)
        if num_subs > 0:
            cleaned_name = new_name.strip()
            if 'manga' in pattern.lower():
                break
    return cleaned_name.strip() if cleaned_name else nome_manga_str


def extrair_nome_manga(base_url):
    partes = urlparse(base_url).path.strip('/').split('/')
    for i in partes[::-1]:
        if i and 'capitulo' not in i.lower() and 'chap' not in i.lower():
            nome_bruto = i.replace('-', ' ').title()
            return nome_bruto
    return 'Manga Desconhecido'

