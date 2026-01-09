"""
PDF Generator Service - Serviço para gerar PDFs a partir de imagens
"""
import os
from typing import List
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
        
        # Carrega todas as imagens como PIL Image
        imagens_pil = []
        
        for caminho in caminhos_imagens:
            try:
                img = Image.open(caminho)
                
                # Converte para RGB se necessário
                if img.mode == 'P' and 'transparency' in img.info:
                    img = img.convert('RGBA')
                
                if img.mode == 'RGBA':
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    imagens_pil.append(background)
                else:
                    imagens_pil.append(img.convert("RGB"))
                    
            except Exception as e:
                raise ImagensInvalidasException(f"Erro ao processar imagem {caminho}: {e}")
        
        if not imagens_pil:
            raise ImagensInvalidasException("Nenhuma imagem válida para gerar PDF")
        
        # Garante que diretório existe
        os.makedirs(os.path.dirname(caminho_pdf_saida), exist_ok=True)
        
        try:
            # Salva primeira imagem com as demais anexadas
            imagens_pil[0].save(
                caminho_pdf_saida,
                save_all=True,
                append_images=imagens_pil[1:] if len(imagens_pil) > 1 else [],
                resolution=self.resolution,
                title=titulo
            )
            
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