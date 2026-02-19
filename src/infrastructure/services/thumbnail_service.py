"""
Thumbnail Service - Serviço para gerar thumbnails de PDFs
"""
import os
import fitz  # PyMuPDF
from PIL import Image

from ...domain.exceptions import ArquivoNaoEncontradoException


class ThumbnailService:
    """
    Serviço responsável por gerar thumbnails de PDFs.
    
    Responsabilidades:
    - Extrair primeira página de PDF
    - Gerar imagem thumbnail
    - Otimizar qualidade/tamanho
    """
    
    def __init__(self, quality: int = 50, scale: float = 2.0, pagina: int = 0):
        """
        Args:
            quality: Qualidade JPEG (0-100)
            scale: Escala de renderização (maior = melhor qualidade)
            pagina: Número da página a usar como thumbnail (0-indexed)
        """
        self.quality = quality
        self.scale = scale
        self.pagina = pagina
    
    def gerar_thumbnail(
        self,
        caminho_pdf: str,
        caminho_thumbnail: str
    ) -> str:
        """
        Gera thumbnail de um PDF.
        
        Args:
            caminho_pdf: Caminho do PDF
            caminho_thumbnail: Caminho onde salvar thumbnail (.jpg)
            
        Returns:
            Caminho do thumbnail gerado
            
        Raises:
            ArquivoNaoEncontradoException: Se PDF não existir
        """
        if not os.path.exists(caminho_pdf):
            raise ArquivoNaoEncontradoException(caminho_pdf)
        
        # Se thumbnail já existe, não recria (cache)
        if os.path.exists(caminho_thumbnail):
            return caminho_thumbnail
        
        try:
            # Abre PDF
            doc = fitz.open(caminho_pdf)
            
            # Verifica se tem páginas
            if doc.page_count == 0:
                doc.close()
                raise ValueError(f"PDF '{caminho_pdf}' não tem páginas")
            
            # Usa página especificada (ou 0 se não existir)
            pagina_idx = min(self.pagina, doc.page_count - 1)
            page = doc.load_page(pagina_idx)
            
            # Renderiza página como imagem
            matriz = fitz.Matrix(self.scale, self.scale)
            pix = page.get_pixmap(matrix=matriz)
            
            # Garante que diretório existe
            os.makedirs(os.path.dirname(caminho_thumbnail), exist_ok=True)
            
            # Converte Pixmap para PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Salva como JPEG com compressão
            img.save(caminho_thumbnail, "JPEG", quality=self.quality, optimize=True)
            
            doc.close()
            
            return caminho_thumbnail
            
        except Exception as e:
            raise Exception(f"Erro ao gerar thumbnail para {caminho_pdf}: {e}")
    
    def gerar_thumbnail_auto(
        self,
        caminho_pdf: str,
        pasta_destino: str
    ) -> str:
        """
        Gera thumbnail com nome automático baseado no PDF.
        
        Args:
            caminho_pdf: Caminho do PDF
            pasta_destino: Pasta onde salvar thumbnail
            
        Returns:
            Caminho do thumbnail gerado
        """
        # Nome do thumbnail baseado no PDF
        nome_pdf = os.path.basename(caminho_pdf)
        nome_thumb = nome_pdf.replace('.pdf', '.jpg')
        caminho_thumb = os.path.join(pasta_destino, nome_thumb)
        
        return self.gerar_thumbnail(caminho_pdf, caminho_thumb)