"""
Image Download Service - Serviço para download de imagens de capítulos
"""
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Optional
from PIL import Image, UnidentifiedImageError
from io import BytesIO

from ...domain.exceptions import DownloadFailedException, ImagensInvalidasException
from ...domain.validators import ValidadorCapitulo


class ImageDownloadService:
    """
    Serviço responsável por baixar imagens de capítulos de mangá.
    
    Responsabilidades:
    - Fazer requisição HTTP para página do capítulo
    - Parsear HTML e extrair URLs de imagens
    - Baixar imagens
    - Validar se imagens são páginas válidas do capítulo
    """
    
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                     "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    def __init__(self, timeout: int = 20):
        """
        Args:
            timeout: Timeout para requisições HTTP em segundos
        """
        self.timeout = timeout
        self.headers = self.DEFAULT_HEADERS.copy()
    
    def baixar_html(self, url: str) -> str:
        """
        Baixa o HTML de uma URL.
        
        Args:
            url: URL da página
            
        Returns:
            Conteúdo HTML da página
            
        Raises:
            DownloadFailedException: Se falhar ao acessar a URL
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            raise DownloadFailedException(url, str(e))
    
    def extrair_urls_imagens(self, html: str, url_base: str) -> List[str]:
        """
        Extrai URLs de imagens do HTML.
        
        Args:
            html: Conteúdo HTML
            url_base: URL base para resolver URLs relativas
            
        Returns:
            Lista de URLs de imagens válidas
        """
        soup = BeautifulSoup(html, 'html.parser')
        tags_imagens = soup.find_all('img')
        
        urls_validas = []
        
        for tag in tags_imagens:
            img_url = self._extrair_url_da_tag(tag, url_base)
            
            if img_url and ValidadorCapitulo.validar_url_imagem(img_url):
                urls_validas.append(img_url)
        
        return urls_validas
    
    def _extrair_url_da_tag(self, tag, url_base: str) -> Optional[str]:
        """
        Extrai URL de uma tag <img>.
        
        Args:
            tag: Tag BeautifulSoup
            url_base: URL base
            
        Returns:
            URL completa da imagem ou None
        """
        # Ordem de prioridade de atributos
        atributos = ["data-src", "src", "data-lazy-src", "data-original", "data-lazyload"]
        
        for attr in atributos:
            src = tag.get(attr)
            if src and isinstance(src, str):
                src = src.strip()
                # Ignora data URIs
                if src and not src.startswith("data:image"):
                    return urljoin(url_base, src)
        
        return None
    
    def baixar_imagem(self, url: str) -> Image.Image:
        """
        Baixa uma imagem e retorna como objeto PIL.
        
        Args:
            url: URL da imagem
            
        Returns:
            Objeto PIL.Image
            
        Raises:
            DownloadFailedException: Se falhar ao baixar
            ImagensInvalidasException: Se não for uma imagem válida
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout, stream=True)
            response.raise_for_status()
            
            # Verifica Content-Type — aceita octet-stream pois alguns servidores
            # servem imagens com tipo binário genérico; o PIL valida o conteúdo real
            content_type = response.headers.get('Content-Type', '').lower()
            if not content_type.startswith('image/') and 'octet-stream' not in content_type:
                raise ImagensInvalidasException(f"Content-Type inválido: {content_type}")
            
            img_data = response.content
            response.close()
            if not img_data:
                raise ImagensInvalidasException("Imagem vazia")

            # Converte para PIL Image
            try:
                buf = BytesIO(img_data)
                del img_data
                img = Image.open(buf)
                img.load()  # força leitura completa antes de fechar o buffer
                buf.close()

                # Converte para RGB se necessário
                if img.mode == 'P' and 'transparency' in img.info:
                    img = img.convert('RGBA')

                if img.mode == 'RGBA':
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img.close()
                    return background

                return img.convert("RGB")
                
            except UnidentifiedImageError:
                raise ImagensInvalidasException(f"Não foi possível identificar a imagem: {url}")
                
        except requests.exceptions.RequestException as e:
            raise DownloadFailedException(url, str(e))
    
    def baixar_imagem_para_disco(self, url: str, caminho_destino: str, referer: str = '') -> str:
        """
        Baixa imagem diretamente para disco via streaming, sem carregar em memória.

        Args:
            url: URL da imagem
            caminho_destino: Caminho completo onde salvar o arquivo
            referer: Header Referer a enviar (necessário em alguns servidores)

        Returns:
            caminho_destino

        Raises:
            DownloadFailedException: Se falhar ao baixar
            ImagensInvalidasException: Se Content-Type inválido ou arquivo muito pequeno
        """
        try:
            headers = self.headers.copy()
            if referer:
                headers['Referer'] = referer

            response = requests.get(url, headers=headers, timeout=self.timeout, stream=True)
            response.raise_for_status()

            content_type = response.headers.get('Content-Type', '').lower()
            if not content_type.startswith('image/') and 'octet-stream' not in content_type:
                raise ImagensInvalidasException(f"Content-Type inválido: {content_type}")

            with open(caminho_destino, 'wb') as f:
                tamanho = 0
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    tamanho += len(chunk)

            if tamanho < 1024:
                os.remove(caminho_destino)
                raise ImagensInvalidasException(
                    f"Arquivo muito pequeno ({tamanho} bytes) — provavelmente não é uma imagem"
                )

            return caminho_destino

        except requests.exceptions.RequestException as e:
            raise DownloadFailedException(url, str(e))

    def baixar_capitulo_completo(
        self, 
        url_capitulo: str,
        pasta_temp: str,
        prefixo_arquivo: str = "page"
    ) -> List[str]:
        """
        Baixa todas as imagens de um capítulo.
        
        Args:
            url_capitulo: URL da página do capítulo
            pasta_temp: Pasta temporária para salvar imagens
            prefixo_arquivo: Prefixo para nomes dos arquivos
            
        Returns:
            Lista de caminhos das imagens baixadas (ordenadas)
            
        Raises:
            DownloadFailedException: Se falhar ao baixar página
            ImagensInvalidasException: Se não houver imagens válidas
        """
        # Baixa HTML
        html = self.baixar_html(url_capitulo)

        # Extrai URLs
        urls_imagens = self.extrair_urls_imagens(html, url_capitulo)

        if not urls_imagens:
            raise ImagensInvalidasException("Nenhuma URL de imagem encontrada na página")

        # Extrai domínio como Referer (alguns servidores exigem para servir imagens)
        parsed = urlparse(url_capitulo)
        referer = f"{parsed.scheme}://{parsed.netloc}/"

        # Cria pasta temp se não existir
        os.makedirs(pasta_temp, exist_ok=True)

        # Baixa cada imagem
        caminhos_salvos = []

        for idx, url in enumerate(urls_imagens):
            try:
                extensao = self._detectar_extensao(url)
                nome_arquivo = f"{prefixo_arquivo}_{str(idx).zfill(3)}{extensao}"
                caminho_completo = os.path.join(pasta_temp, nome_arquivo)
                self.baixar_imagem_para_disco(url, caminho_completo, referer=referer)
                caminhos_salvos.append(caminho_completo)
            except (DownloadFailedException, ImagensInvalidasException) as e:
                print(f"Erro ao baixar {url}: {e}")
                continue
        
        # Valida quantidade mínima
        valido, mensagem = ValidadorCapitulo.validar_quantidade_minima(len(caminhos_salvos))
        if not valido:
            raise ImagensInvalidasException(mensagem)
        
        # Retorna ordenado
        return sorted(caminhos_salvos)
    
    def _detectar_extensao(self, url: str) -> str:
        """
        Detecta extensão da imagem pela URL.
        
        Args:
            url: URL da imagem
            
        Returns:
            Extensão (.jpg, .png, .webp)
        """
        nome_arquivo = os.path.basename(urlparse(url).path).lower()
        
        if nome_arquivo.endswith('.png'):
            return '.png'
        elif nome_arquivo.endswith('.webp'):
            return '.webp'
        elif nome_arquivo.endswith(('.jpg', '.jpeg')):
            return '.jpg'
        else:
            return '.jpg'  # default