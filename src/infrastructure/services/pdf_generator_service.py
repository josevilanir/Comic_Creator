"""
PDF Generator Service - Serviço para gerar PDFs a partir de imagens
"""
import os
from typing import List
import fitz  # pymupdf
from PIL import Image

from ...domain.exceptions import ImagensInvalidasException


class PDFGeneratorService:
    """
    Serviço responsável por gerar arquivos PDF a partir de imagens.
    
    Responsabilidades:
    - Converter lista de imagens em PDF
    - Otimizar tamanho do PDF
    - Adicionar metadados
    """
    
    def __init__(self, resolution: float = 100.0, quality: int = 95):
        """
        Args:
            resolution: Resolução do PDF (DPI)
            quality: Qualidade de compressão JPEG (0-100)
        """
        self.resolution = resolution
        self.quality = quality
    
    def gerar_pdf_de_imagens(
        self,
        caminhos_imagens: List[str],
        caminho_pdf_saida: str,
        titulo: str = "Comic"
    ) -> str:
        """
        Gera um PDF a partir de uma lista de imagens.
        
        Args:
            caminhos_imagens: Lista de caminhos das imagens (ordenados)
            caminho_pdf_saida: Caminho onde salvar o PDF
            titulo: Título do PDF (metadado)
            
        Returns:
            Caminho do PDF gerado
            
        Raises:
            ImagensInvalidasException: Se não houver imagens ou erro ao gerar
        """
        if not caminhos_imagens:
            raise ImagensInvalidasException("Nenhuma imagem fornecida para gerar PDF")

        # Garante que diretório existe
        os.makedirs(os.path.dirname(caminho_pdf_saida), exist_ok=True)

        try:
            doc = fitz.open()
            for caminho in caminhos_imagens:
                # Converte cada imagem para um PDF de uma página e insere no doc.
                # PyMuPDF processa uma imagem por vez — sem acumular todas em RAM.
                with fitz.open(caminho) as img_doc:
                    pdf_bytes = img_doc.convert_to_pdf()
                page_pdf = fitz.open("pdf", pdf_bytes)
                doc.insert_pdf(page_pdf)
                page_pdf.close()

            doc.set_metadata({"title": titulo})
            doc.save(caminho_pdf_saida, garbage=4, deflate=True)
            doc.close()
            return caminho_pdf_saida

        except Exception as e:
            raise ImagensInvalidasException(f"Erro ao salvar PDF: {e}")
    
    def gerar_pdf_de_imagens_pil(
        self,
        imagens_pil: List[Image.Image],
        caminho_pdf_saida: str,
        titulo: str = "Comic"
    ) -> str:
        """
        Gera PDF diretamente de objetos PIL.Image.
        
        Args:
            imagens_pil: Lista de objetos PIL.Image (já em RGB)
            caminho_pdf_saida: Caminho de saída
            titulo: Título do PDF
            
        Returns:
            Caminho do PDF gerado
        """
        if not imagens_pil:
            raise ImagensInvalidasException("Nenhuma imagem fornecida")
        
        # Garante que todas são RGB
        imagens_rgb = []
        for img in imagens_pil:
            if img.mode != 'RGB':
                imagens_rgb.append(img.convert('RGB'))
            else:
                imagens_rgb.append(img)
        
        # Garante diretório
        os.makedirs(os.path.dirname(caminho_pdf_saida), exist_ok=True)
        
        try:
            imagens_rgb[0].save(
                caminho_pdf_saida,
                save_all=True,
                append_images=imagens_rgb[1:] if len(imagens_rgb) > 1 else [],
                resolution=self.resolution,
                title=titulo
            )
            
            return caminho_pdf_saida
            
        except Exception as e:
            raise ImagensInvalidasException(f"Erro ao salvar PDF: {e}")