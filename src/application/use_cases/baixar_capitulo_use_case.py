"""
Baixar Capitulo Use Case - Caso de uso para baixar capítulos de mangá isolados por usuário
"""
import os
import re
import shutil
import tempfile
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional, List, Tuple
from urllib.parse import urljoin, urlparse, parse_qs

from ...domain.entities import Capitulo, Manga
from ...domain.repositories import IMangaRepository, ICapituloRepository
from ...domain.exceptions import (
    ImagensInvalidasException,
    DownloadFailedException
)
from ...infrastructure.services import (
    ImageDownloadService,
    PDFGeneratorService,
    ThumbnailService
)


@dataclass
class BaixarCapituloDTO:
    """DTO para entrada do use case"""
    url_capitulo: str
    nome_manga: str
    numero_capitulo: int
    sobrescrever: bool = False


@dataclass
class BaixarCapituloResultado:
    """DTO para resultado do use case"""
    sucesso: bool
    mensagem: str
    capitulo: Optional[Capitulo] = None
    caminho_pdf: Optional[str] = None


# ── Constantes ────────────────────────────────────────────────────────────────
_PADDINGS = [None, 2, 3]
_MIN_IMAGENS_CAPITULO = 10
_HEADERS = { "User-Agent": "Mozilla/5.0" }
_EXTENSOES_IMAGEM = ('.jpg', '.jpeg', '.png', '.webp')
_BLACKLIST_UI = ['logo', 'banner', 'icon', 'favicon', 'button', 'badge', 'spinner', 'loading', 'placeholder']
_CDN_SEQUENCIAL_RE = re.compile(r'^(https?://.+/)(\d{2,3})\.(jpg|jpeg|png|webp)$', re.IGNORECASE)


def _aplicar_padding(url: str, numero: int, largura: Optional[int]) -> str:
    if largura is None: return url
    num_formatado = str(numero).zfill(largura)
    return re.sub(r'(\d+)(/?$)', lambda m: f"{num_formatado}{m.group(2)}", url)


def _extrair_imgs_de_pagina(html: str, url_base: str) -> List[str]:
    soup = BeautifulSoup(html, 'html.parser')
    atributos_src = ['data-src', 'src', 'data-lazy-src', 'data-original', 'data-lazyload']
    urls: List[str] = []
    for tag in soup.find_all('img'):
        for attr in atributos_src:
            src = tag.get(attr, '')
            if not src or not isinstance(src, str) or src.startswith('data:'): continue
            url_completa = urljoin(url_base, src.strip())
            caminho_sem_query = url_completa.split('?')[0].lower()
            if not any(caminho_sem_query.endswith(ext) for ext in _EXTENSOES_IMAGEM): continue
            if any(palavra in caminho_sem_query.split('/')[-1] for palavra in _BLACKLIST_UI): continue
            urls.append(url_completa)
            break

    # Extrai imagens de links de redirect (ex: Madara theme com suaap.com?t=IMAGE_URL)
    for tag in soup.find_all('a', href=True):
        try:
            params = parse_qs(urlparse(tag['href']).query)
            if 't' in params:
                img_url = params['t'][0]
                caminho = img_url.split('?')[0].lower()
                if any(caminho.endswith(e) for e in _EXTENSOES_IMAGEM) and \
                   not any(p in caminho.split('/')[-1] for p in _BLACKLIST_UI):
                    urls.append(img_url)
        except Exception:
            pass

    visto, unicas = set(), []
    for u in urls:
        if u not in visto:
            visto.add(u)
            unicas.append(u)

    # Sites com lazy-load (ex: Madara) expõem só a 1ª página no HTML estático.
    # Se o padrão CDN sequencial for detectado, enumera todas as páginas.
    if len(unicas) < _MIN_IMAGENS_CAPITULO and unicas:
        cdn = _enumerar_cdn_sequencial(unicas)
        if cdn:
            return cdn

    return unicas


def _enumerar_cdn_sequencial(seeds: List[str]) -> List[str]:
    """Enumera páginas via CDN sequencial (01.jpg, 02.jpg...) quando o HTML só expõe a primeira."""
    for seed in seeds:
        m = _CDN_SEQUENCIAL_RE.match(seed.split('?')[0])
        if not m:
            continue
        base, num_str, ext = m.group(1), m.group(2), m.group(3)
        largura = len(num_str)
        result = []
        for i in range(1, 100):
            url = f"{base}{str(i).zfill(largura)}.{ext}"
            try:
                resp = requests.head(url, headers=_HEADERS, timeout=8, allow_redirects=True)
                if resp.status_code >= 400:
                    break
                result.append(url)
            except Exception:
                break
        if len(result) >= _MIN_IMAGENS_CAPITULO:
            return result
    return []


def _verificar_conteudo_url(url: str, timeout: int = 12) -> Tuple[bool, List[str]]:
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=timeout, allow_redirects=True)
        if resp.status_code >= 400: return False, []
        urls_imagens = _extrair_imgs_de_pagina(resp.text, url)
        return len(urls_imagens) >= _MIN_IMAGENS_CAPITULO, urls_imagens
    except Exception: return False, []


class BaixarCapituloUseCase:
    def __init__(
        self,
        manga_repo: IMangaRepository,
        capitulo_repo: ICapituloRepository,
        image_service: ImageDownloadService,
        pdf_service: PDFGeneratorService,
        thumbnail_service: ThumbnailService,
        base_dir: str
    ):
        self.manga_repo = manga_repo
        self.capitulo_repo = capitulo_repo
        self.image_service = image_service
        self.pdf_service = pdf_service
        self.thumbnail_service = thumbnail_service
        self.base_dir = base_dir

    def executar(self, dto: BaixarCapituloDTO, user_id: int) -> BaixarCapituloResultado:
        try:
            url = dto.url_capitulo.strip()
            if not url.startswith(('http://', 'https://')):
                return BaixarCapituloResultado(False, "URL inválida")

            if not dto.sobrescrever and self.capitulo_repo.existe(user_id, dto.nome_manga, dto.numero_capitulo):
                return BaixarCapituloResultado(False, f"Capítulo {dto.numero_capitulo} já existe")

            url_resolvida, urls_imagens = self._resolver_url_com_conteudo(url, dto.numero_capitulo)
            if url_resolvida is None:
                return BaixarCapituloResultado(False, f"Capítulo {dto.numero_capitulo} não encontrado")

            manga = self.manga_repo.buscar_por_nome(user_id, dto.nome_manga)
            if not manga:
                manga = Manga(nome=dto.nome_manga, caminho="PENDING")
                manga = self.manga_repo.salvar(user_id, manga)

            # Todo trabalho local ocorre em um diretório temporário isolado.
            # O repositório de capítulos é responsável por mover/fazer upload
            # para o destino final (filesystem ou S3).
            pasta_temp = tempfile.mkdtemp()
            try:
                caminhos_imagens = self.image_service.baixar_capitulo_completo(
                    url_resolvida, pasta_temp, prefixo_arquivo=f"cap{dto.numero_capitulo}"
                )
                if len(caminhos_imagens) < _MIN_IMAGENS_CAPITULO:
                    raise ImagensInvalidasException("Imagens insuficientes salvas.")

                nome_pdf = f"capitulo_{str(dto.numero_capitulo).zfill(3)}.pdf"
                caminho_pdf = os.path.join(pasta_temp, nome_pdf)
                self.pdf_service.gerar_pdf_de_imagens(
                    caminhos_imagens, caminho_pdf, titulo=f"{dto.nome_manga} - Cap. {dto.numero_capitulo}"
                )

                caminho_thumb = caminho_pdf.replace(".pdf", ".jpg")
                self.thumbnail_service.gerar_thumbnail(caminho_pdf, caminho_thumb)

                capitulo = Capitulo(
                    numero=dto.numero_capitulo,
                    nome_arquivo=nome_pdf,
                    manga_nome=dto.nome_manga,
                    caminho_completo=caminho_pdf,
                )
                capitulo = self.capitulo_repo.salvar(user_id, capitulo)

                return BaixarCapituloResultado(True, f"Capítulo {dto.numero_capitulo} baixado!", capitulo, caminho_pdf)

            except Exception as e:
                raise e
            finally:
                shutil.rmtree(pasta_temp, ignore_errors=True)

        except Exception as e:
            return BaixarCapituloResultado(False, f"Erro: {str(e)}")

    def _resolver_url_com_conteudo(self, url_original: str, numero: int) -> Tuple[Optional[str], List[str]]:
        import logging
        logger = logging.getLogger(__name__)
        for largura in _PADDINGS:
            url_candidata = _aplicar_padding(url_original, numero, largura)
            logger.info(f"Tentando resolver URL: {url_candidata}")
            tem_conteudo, urls_imagens = _verificar_conteudo_url(url_candidata)
            if tem_conteudo: 
                logger.info(f"URL resolvida com sucesso: {url_candidata} ({len(urls_imagens)} imagens)")
                return url_candidata, urls_imagens
        logger.warning(f"Não foi possível resolver conteúdo para capítulo {numero} na URL base: {url_original}")
        return None, []
