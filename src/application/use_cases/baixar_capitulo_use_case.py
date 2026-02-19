"""
Baixar Capitulo Use Case - Caso de uso para baixar capítulos de mangá
"""
import os
import shutil
from dataclasses import dataclass
from typing import Optional

from ...domain.entities import Capitulo, Manga
from ...domain.repositories import IMangaRepository, ICapituloRepository
from ...domain.validators import ValidadorURL, ValidadorCapitulo
from ...domain.exceptions import (
    CapituloJaExisteException,
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


class BaixarCapituloUseCase:
    """
    Caso de uso para baixar um capítulo de mangá.
    
    Fluxo:
    1. Valida URL
    2. Verifica se capítulo já existe
    3. Cria pasta do mangá se não existir
    4. Baixa imagens
    5. Valida se imagens são páginas de capítulo
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
    
    def executar(self, dto: BaixarCapituloDTO) -> BaixarCapituloResultado:
        """
        Executa o caso de uso de baixar capítulo.
        
        Args:
            dto: Dados de entrada
            
        Returns:
            Resultado do download
        """
        try:
            # 1. Valida URL
            valido, mensagem = ValidadorURL.validar_url_base(dto.url_capitulo)
            if not valido:
                return BaixarCapituloResultado(
                    sucesso=False,
                    mensagem=f"URL inválida: {mensagem}"
                )
            
            # 2. Verifica se capítulo já existe
            if not dto.sobrescrever:
                if self.capitulo_repo.existe(dto.nome_manga, dto.numero_capitulo):
                    return BaixarCapituloResultado(
                        sucesso=False,
                        mensagem=f"Capítulo {dto.numero_capitulo} de '{dto.nome_manga}' já existe"
                    )
            
            # 3. Garante que mangá existe no repositório
            manga = self.manga_repo.buscar_por_nome(dto.nome_manga)
            if not manga:
                manga = Manga(
                    nome=dto.nome_manga,
                    caminho=os.path.join(self.base_dir, dto.nome_manga)
                )
                manga = self.manga_repo.salvar(manga)
            
            # 4. Cria pasta temporária para imagens
            pasta_temp = os.path.join(manga.caminho, "tmp")
            os.makedirs(pasta_temp, exist_ok=True)
            
            try:
                # 5. Baixa imagens
                print(f"Baixando imagens de {dto.url_capitulo}...")
                caminhos_imagens = self.image_service.baixar_capitulo_completo(
                    dto.url_capitulo,
                    pasta_temp,
                    prefixo_arquivo=f"cap{dto.numero_capitulo}"
                )
                
                # 6. Valida quantidade
                valido, msg_validacao = ValidadorCapitulo.validar_quantidade_minima(
                    len(caminhos_imagens)
                )
                if not valido:
                    raise ImagensInvalidasException(msg_validacao)
                
                print(f"✓ {len(caminhos_imagens)} imagens baixadas e validadas")
                
                # 7. Gera PDF
                nome_pdf = f"capitulo_{str(dto.numero_capitulo).zfill(3)}.pdf"
                caminho_pdf = os.path.join(manga.caminho, nome_pdf)
                
                print(f"Gerando PDF: {nome_pdf}...")
                self.pdf_service.gerar_pdf_de_imagens(
                    caminhos_imagens,
                    caminho_pdf,
                    titulo=f"{dto.nome_manga} - Capítulo {dto.numero_capitulo}"
                )
                
                print(f"✓ PDF criado: {caminho_pdf}")
                
                # 8. Gera thumbnail
                print("Gerando thumbnail...")
                self.thumbnail_service.gerar_thumbnail_auto(caminho_pdf, manga.caminho)
                print("✓ Thumbnail criado")
                
                # 9. Cria entidade Capitulo
                capitulo = Capitulo(
                    numero=dto.numero_capitulo,
                    nome_arquivo=nome_pdf,
                    manga_nome=dto.nome_manga,
                    caminho_completo=caminho_pdf
                )
                
                # 10. Salva no repositório
                capitulo = self.capitulo_repo.salvar(capitulo)
                
                # 11. Limpa temporários
                if os.path.exists(pasta_temp):
                    shutil.rmtree(pasta_temp)
                    print("✓ Arquivos temporários removidos")
                
                return BaixarCapituloResultado(
                    sucesso=True,
                    mensagem=f"Capítulo {dto.numero_capitulo} baixado com sucesso!",
                    capitulo=capitulo,
                    caminho_pdf=caminho_pdf
                )
                
            except (ImagensInvalidasException, DownloadFailedException) as e:
                # Limpa temporários em caso de erro
                if os.path.exists(pasta_temp):
                    shutil.rmtree(pasta_temp)
                
                return BaixarCapituloResultado(
                    sucesso=False,
                    mensagem=str(e)
                )
                
        except Exception as e:
            return BaixarCapituloResultado(
                sucesso=False,
                mensagem=f"Erro inesperado: {str(e)}"
            )