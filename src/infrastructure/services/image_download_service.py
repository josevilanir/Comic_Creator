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
            
            # Verifica Content-Type
            content_type = response.headers.get('Content-Type', '').lower()
            if not content_type.startswith('image/'):
                raise ImagensInvalidasException(f"Content-Type inválido: {content_type}")
            
            img_data = response.content
            if not img_data:
                raise ImagensInvalidasException("Imagem vazia")
            
            # Converte para PIL Image
            try:
                img = Image.open(BytesIO(img_data))
                
                # Converte para RGB se necessário
                if img.mode == 'P' and 'transparency' in img.info:
                    img = img.convert('RGBA')
                
                if img.mode == 'RGBA':
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    return background
                
                return img.convert("RGB")
                
            except UnidentifiedImageError:
                raise ImagensInvalidasException(f"Não foi possível identificar a imagem: {url}")
                
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
        
        # Cria pasta temp se não existir
        os.makedirs(pasta_temp, exist_ok=True)
        
        # Baixa cada imagem
        caminhos_salvos = []
        
        for idx, url in enumerate(urls_imagens):
            try:
                img = self.baixar_imagem(url)
                
                # Detecta extensão pelo Content-Type ou URL
                extensao = self._detectar_extensao(url)
                nome_arquivo = f"{prefixo_arquivo}_{str(idx).zfill(3)}{extensao}"
                caminho_completo = os.path.join(pasta_temp, nome_arquivo)
                
                # Salva como RGB
                if extensao == '.jpg':
                    img.save(caminho_completo, 'JPEG', quality=95)
                elif extensao == '.png':
                    img.save(caminho_completo, 'PNG')
                elif extensao == '.webp':
                    img.save(caminho_completo, 'WEBP', quality=95)
                else:
                    img.save(caminho_completo, 'JPEG', quality=95)
                
                caminhos_salvos.append(caminho_completo)
                
            except (DownloadFailedException, ImagensInvalidasException) as e:
                # Log erro mas continua tentando outras imagens
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