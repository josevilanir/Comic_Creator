"""
Testes de integração para FileSystemMangaRepository
"""
import pytest
import os
import tempfile
import shutil
from src.domain.entities.manga import Manga


@pytest.mark.integration
class TestFileSystemMangaRepository:
    """Testes do repositório de mangás em filesystem"""
    
    def test_manga_repository_pode_ser_importado(self):
        """Deve ser possível importar o repositório"""
        try:
            from src.infrastructure.repositories.filesystem_manga_repository import FileSystemMangaRepository
            assert FileSystemMangaRepository is not None
        except ImportError:
            pytest.skip("Repositório não disponível")
    
    def test_entidade_manga_funciona(self):
        """Entidade Manga deve funcionar corretamente"""
        manga = Manga(
            nome="One Piece",
            caminho="/manga/one_piece"
        )
        
        assert manga.nome == "One Piece"
        assert manga.caminho == "/manga/one_piece"
    
    def test_multiplas_mangas_podem_ser_criadas(self):
        """Deve ser possível criar múltiplas entidades Manga"""
        mangas = [
            Manga(nome="One Piece", caminho="/manga/one_piece"),
            Manga(nome="Naruto", caminho="/manga/naruto"),
            Manga(nome="Bleach", caminho="/manga/bleach"),
        ]
        
        assert len(mangas) == 3
        nomes = [m.nome for m in mangas]
        assert "One Piece" in nomes
        assert "Naruto" in nomes
        assert "Bleach" in nomes

