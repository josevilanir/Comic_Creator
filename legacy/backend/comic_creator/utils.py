import json
import os
import re
from urllib.parse import urlparse
from flask import current_app


def carregar_urls():
    # Try multiple candidate locations for the saved URLs file to be robust
    candidates = []
    cfg_path = current_app.config.get('URLS_JSON')
    if cfg_path:
        candidates.append(os.path.abspath(cfg_path))
    # project root (where main.py lives)
    candidates.append(os.path.abspath(os.path.join(os.getcwd(), 'urls_salvas.json')))
    # relative to this package
    candidates.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'urls_salvas.json')))

    for path in candidates:
        try:
            if path and os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        # if we found a valid file, ensure app config points to it
                        current_app.config['URLS_JSON'] = path
                        return data
                    except json.JSONDecodeError:
                        current_app.logger.error(f'Erro ao decodificar {path}.')
                        return {}
        except Exception as e:
            current_app.logger.debug(f'Erro ao acessar {path}: {e}')
    return {}


def salvar_urls(urls):
    path = current_app.config.get('URLS_JSON') or os.path.join(os.getcwd(), 'urls_salvas.json')
    path = os.path.abspath(path)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(urls, f, indent=4, ensure_ascii=False)
        current_app.config['URLS_JSON'] = path
    except Exception as e:
        current_app.logger.error(f'Erro ao salvar {path}: {e}')


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
