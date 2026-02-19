"""
Testes unitários para entidade Manga
"""
import pytest
import tempfile
from src.domain.entities.manga import Manga


@pytest.mark.unit
class TestMangaEntity:
    """Testes da entidade Manga"""
    
    def test_criar_manga_valido(self):
        """Deve criar mangá com dados válidos"""
        manga = Manga(
            nome="One Piece",
            caminho="/tmp/one_piece",
            tem_capa=True,
            total_capitulos=10
        )
        
        assert manga.nome == "One Piece"
        assert manga.caminho == "/tmp/one_piece"
        assert manga.tem_capa is True
        assert manga.total_capitulos == 10
    
    def test_manga_sem_capa(self):
        """Deve criar mangá sem capa"""
        manga = Manga(
            nome="Naruto",
            caminho="/tmp/naruto",
            tem_capa=False,
            total_capitulos=0
        )
        
        assert manga.tem_capa is False
        assert manga.total_capitulos == 0
    
    def test_manga_nome_vazio_deve_falhar(self):
        """Não deve aceitar nome vazio"""
        with pytest.raises(ValueError, match="Nome do mangá não pode ser vazio"):
            Manga(nome="", caminho="/tmp/test", tem_capa=False, total_capitulos=0)
    
    def test_manga_nome_apenas_espacos_deve_falhar(self):
        """Não deve aceitar nome com apenas espaços"""
        with pytest.raises(ValueError, match="Nome do mangá não pode ser vazio"):
            Manga(nome="   ", caminho="/tmp/test", tem_capa=False, total_capitulos=0)
    
    def test_manga_caminho_vazio_deve_falhar(self):
        """Não deve aceitar caminho vazio"""
        with pytest.raises(ValueError, match="Caminho do mangá não pode ser vazio"):
            Manga(nome="Test", caminho="", tem_capa=False, total_capitulos=0)
    
    def test_adicionar_capitulo(self):
        """Deve incrementar contador de capítulos"""
        manga = Manga(
            nome="Test",
            caminho="/tmp/test",
            total_capitulos=5
        )
        
        manga.adicionar_capitulo()
        
        assert manga.total_capitulos == 6
    
    def test_remover_capitulo(self):
        """Deve decrementar contador de capítulos"""
        manga = Manga(
            nome="Test",
            caminho="/tmp/test",
            total_capitulos=5
        )
        
        manga.remover_capitulo()
        
        assert manga.total_capitulos == 4
    
    def test_remover_capitulo_nao_pode_ficar_negativo(self):
        """Decremento não pode resultar em negativo"""
        manga = Manga(
            nome="Test",
            caminho="/tmp/test",
            total_capitulos=0
        )
        
        manga.remover_capitulo()
        
        assert manga.total_capitulos == 0
    
    def test_nome_normalizado_remove_espacos(self):
        """Nome deve ser normalizado removendo espaços"""
        manga = Manga(
            nome="  One Piece  ",
            caminho="/tmp/one_piece"
        )
        
        assert manga.nome == "One Piece"
    
    def test_atualizar_capa(self):
        """Deve atualizar URL da capa e marcar como tendo capa"""
        manga = Manga(
            nome="Test",
            caminho="/tmp/test",
            tem_capa=False
        )
        
        assert manga.tem_capa is False
        
        manga.atualizar_capa("https://example.com/capa.jpg")
        
        assert manga.tem_capa is True
        assert manga.capa_url == "https://example.com/capa.jpg"
