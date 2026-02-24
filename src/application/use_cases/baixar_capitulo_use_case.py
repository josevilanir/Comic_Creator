"""
Baixar Capitulo Use Case - Caso de uso para baixar capítulos de mangá
"""
import os
import re
import shutil
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional, List, Tuple
from urllib.parse import urljoin

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

# Variantes de zero-padding a testar, em ordem
_PADDINGS = [None, 2, 3]  # None = sem padding | 2 = "01" | 3 = "001"

# Quantidade mínima de imagens para considerar que a URL tem conteúdo real
_MIN_IMAGENS_CAPITULO = 10

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    )
}

_EXTENSOES_IMAGEM = ('.jpg', '.jpeg', '.png', '.webp')

# Palavras no nome do arquivo que indicam elemento de UI (não é página de capítulo)
_BLACKLIST_UI = [
    'logo', 'banner', 'avatar', 'icon', 'favicon',
    'button', 'badge', 'spinner', 'loading', 'placeholder',
    'social', 'facebook', 'twitter', 'instagram',
    'header', 'footer', 'rating', 'star', 'ads',
    'capa', 'cover-default', 'no-image',
]


# ── Helpers de módulo ─────────────────────────────────────────────────────────

def _aplicar_padding(url: str, numero: int, largura: Optional[int]) -> str:
    """
    Substitui o número no final da URL pelo número com zero-padding.

    Exemplos:
        ("https://site.com/capitulo-1/", 1, 2)    -> "https://site.com/capitulo-01/"
        ("https://site.com/capitulo-1/", 1, 3)    -> "https://site.com/capitulo-001/"
        ("https://site.com/capitulo-1/", 1, None) -> sem alteração
    """
    if largura is None:
        return url
    num_formatado = str(numero).zfill(largura)
    return re.sub(
        r'(\d+)(/?$)',
        lambda m: f"{num_formatado}{m.group(2)}",
        url
    )


def _extrair_imgs_de_pagina(html: str, url_base: str) -> List[str]:
    """
    Varre o HTML e retorna URLs de imagens que parecem páginas de capítulo.

    Critérios de aceitação:
    - Extensão válida (.jpg, .jpeg, .png, .webp)
    - Nome do arquivo NÃO contém palavras de UI (logo, icon, banner...)
    - Não é data URI
    """
    soup = BeautifulSoup(html, 'html.parser')
    atributos_src = ['data-src', 'src', 'data-lazy-src', 'data-original', 'data-lazyload']

    urls: List[str] = []

    for tag in soup.find_all('img'):
        for attr in atributos_src:
            src = tag.get(attr, '')
            if not src or not isinstance(src, str):
                continue
            src = src.strip()

            # Ignora data URIs
            if src.startswith('data:'):
                continue

            url_completa = urljoin(url_base, src)
            caminho_sem_query = url_completa.split('?')[0].lower()

            # Filtra por extensão
            if not any(caminho_sem_query.endswith(ext) for ext in _EXTENSOES_IMAGEM):
                continue

            # Filtra elementos de UI pela blacklist
            nome_arquivo = caminho_sem_query.split('/')[-1]
            if any(palavra in nome_arquivo for palavra in _BLACKLIST_UI):
                continue

            urls.append(url_completa)
            break  # Usa o primeiro atributo válido encontrado nessa tag

    # Remove duplicatas mantendo ordem de aparição
    visto: set = set()
    unicas: List[str] = []
    for u in urls:
        if u not in visto:
            visto.add(u)
            unicas.append(u)

    return unicas


def _verificar_conteudo_url(url: str, timeout: int = 12) -> Tuple[bool, List[str]]:
    """
    Baixa o HTML da URL e verifica se ela contém imagens reais de capítulo.

    Retorna:
        (True,  lista_de_urls_imagens)  — URL tem conteúdo suficiente
        (False, [])                     — URL não tem conteúdo de capítulo
    """
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=timeout, allow_redirects=True)
        if resp.status_code >= 400:
            print(f"    ✗ HTTP {resp.status_code}")
            return False, []

        urls_imagens = _extrair_imgs_de_pagina(resp.text, url)
        quantidade = len(urls_imagens)

        if quantidade >= _MIN_IMAGENS_CAPITULO:
            print(f"    ✓ {quantidade} imagens encontradas")
            return True, urls_imagens

        print(f"    ✗ {quantidade} imagem(ns) — insuficiente (mínimo: {_MIN_IMAGENS_CAPITULO})")
        return False, []

    except Exception as e:
        print(f"    ✗ Erro: {e}")
        return False, []


# ── Use Case ──────────────────────────────────────────────────────────────────

class BaixarCapituloUseCase:
    """
    Caso de uso para baixar um capítulo de mangá.

    Fluxo:
    1. Valida formato básico da URL (http/https)
    2. Verifica se capítulo já existe localmente
    3. Resolve a URL correta testando variantes de zero-padding —
       critério real: a página deve conter >= 3 imagens de capítulo
    4. Garante que o mangá existe no repositório
    5. Baixa as imagens
    6. Gera PDF
    7. Gera thumbnail
    8. Salva no repositório
    9. Limpa arquivos temporários
    """

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

    # ── Público ───────────────────────────────────────────────────────────────

    def executar(self, dto: BaixarCapituloDTO) -> BaixarCapituloResultado:
        """Executa o download de um capítulo com fallback automático de zero-padding."""

        try:
            # 1. Validação de formato básico
            url = dto.url_capitulo.strip()
            if not url.startswith(('http://', 'https://')):
                return BaixarCapituloResultado(
                    sucesso=False,
                    mensagem="URL inválida: deve começar com http:// ou https://"
                )

            # 2. Capítulo já existe?
            if not dto.sobrescrever:
                if self.capitulo_repo.existe(dto.nome_manga, dto.numero_capitulo):
                    return BaixarCapituloResultado(
                        sucesso=False,
                        mensagem=f"Capítulo {dto.numero_capitulo} de '{dto.nome_manga}' já existe"
                    )

            # 3. Resolve URL — testa sem padding, 01, 001 e aceita a primeira
            #    que realmente contém imagens de capítulo no HTML
            url_resolvida, urls_pre_validadas = self._resolver_url_com_conteudo(
                url, dto.numero_capitulo
            )

            if url_resolvida is None:
                return BaixarCapituloResultado(
                    sucesso=False,
                    mensagem=(
                        f"Capítulo {dto.numero_capitulo} não encontrado. "
                        f"Testadas variantes: sem padding, '01' e '001'. "
                        f"Nenhuma URL retornou imagens suficientes."
                    )
                )

            if url_resolvida != url:
                print(f"⚠ Usando URL com zero-padding: {url_resolvida}")

            # 4. Garante mangá no repositório
            manga = self.manga_repo.buscar_por_nome(dto.nome_manga)
            if not manga:
                manga = Manga(
                    nome=dto.nome_manga,
                    caminho=os.path.join(self.base_dir, dto.nome_manga)
                )
                manga = self.manga_repo.salvar(manga)

            # 5. Pasta temporária
            pasta_temp = os.path.join(manga.caminho, "tmp")
            os.makedirs(pasta_temp, exist_ok=True)

            try:
                # 6. Baixa imagens via ImageDownloadService
                print(f"Baixando imagens de {url_resolvida}...")
                caminhos_imagens = self.image_service.baixar_capitulo_completo(
                    url_resolvida,
                    pasta_temp,
                    prefixo_arquivo=f"cap{dto.numero_capitulo}"
                )

                if len(caminhos_imagens) < _MIN_IMAGENS_CAPITULO:
                    raise ImagensInvalidasException(
                        f"Apenas {len(caminhos_imagens)} imagem(ns) salva(s) com sucesso."
                    )

                print(f"✓ {len(caminhos_imagens)} imagens baixadas")

                # 7. Gera PDF
                nome_pdf = f"capitulo_{str(dto.numero_capitulo).zfill(3)}.pdf"
                caminho_pdf = os.path.join(manga.caminho, nome_pdf)

                print(f"Gerando PDF: {nome_pdf}...")
                self.pdf_service.gerar_pdf_de_imagens(
                    caminhos_imagens,
                    caminho_pdf,
                    titulo=f"{dto.nome_manga} - Capítulo {dto.numero_capitulo}"
                )
                print("✓ PDF criado")

                # 8. Gera thumbnail
                self.thumbnail_service.gerar_thumbnail_auto(caminho_pdf, manga.caminho)
                print("✓ Thumbnail criado")

                # 9. Persiste entidade
                capitulo = Capitulo(
                    numero=dto.numero_capitulo,
                    nome_arquivo=nome_pdf,
                    manga_nome=dto.nome_manga,
                    caminho_completo=caminho_pdf
                )
                capitulo = self.capitulo_repo.salvar(capitulo)

                # 10. Limpa temporários
                if os.path.exists(pasta_temp):
                    shutil.rmtree(pasta_temp)
                print("✓ Temporários removidos")

                return BaixarCapituloResultado(
                    sucesso=True,
                    mensagem=f"Capítulo {dto.numero_capitulo} baixado com sucesso!",
                    capitulo=capitulo,
                    caminho_pdf=caminho_pdf
                )

            except (ImagensInvalidasException, DownloadFailedException) as e:
                if os.path.exists(pasta_temp):
                    shutil.rmtree(pasta_temp)
                return BaixarCapituloResultado(sucesso=False, mensagem=str(e))

        except Exception as e:
            return BaixarCapituloResultado(
                sucesso=False,
                mensagem=f"Erro inesperado: {str(e)}"
            )

    # ── Privado ───────────────────────────────────────────────────────────────

    def _resolver_url_com_conteudo(
        self,
        url_original: str,
        numero: int
    ) -> Tuple[Optional[str], List[str]]:
        """
        Testa variantes de zero-padding e retorna a primeira URL que
        contém imagens reais de capítulo (>= _MIN_IMAGENS_CAPITULO).

        Sequência testada:
            capitulo-1/   → sem padding
            capitulo-01/  → padding 2 dígitos
            capitulo-001/ → padding 3 dígitos

        Retorna:
            (url_válida, lista_urls_imagens) — se encontrou conteúdo
            (None, [])                       — se nenhuma variante funcionou
        """
        for largura in _PADDINGS:
            url_candidata = _aplicar_padding(url_original, numero, largura)
            print(f"  → Testando: {url_candidata}")

            tem_conteudo, urls_imagens = _verificar_conteudo_url(url_candidata)

            if tem_conteudo:
                return url_candidata, urls_imagens

        return None, []