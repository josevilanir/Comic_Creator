"""
Testes de integração para casos de uso
"""
import pytest
from src.domain.entities.manga import Manga
from src.domain.entities.capitulo import Capitulo


@pytest.mark.integration
class TestBaixarCapituloUseCase:
    """Testes de integração do caso de uso de baixar capítulo"""
    
    def test_entidades_podem_ser_criadas(self):
        """Deve criar entidades de exemplo corretamente"""
        manga = Manga(
            nome="One Piece",
            caminho="/manga/one_piece"
        )
        
        capitulo = Capitulo(
            manga_nome="One Piece",
            numero=1,
            nome_arquivo="Capitulo_1.pdf",
            caminho_completo="/manga/one_piece/cap_1.pdf"
        )
        
        assert manga.nome == "One Piece"
        assert capitulo.manga_nome == "One Piece"
        assert capitulo.numero == 1
    
    def test_relacao_manga_capitulo(self):
        """Entidades devem manter relação consistente"""
        manga_nome = "Naruto"
        manga = Manga(nome=manga_nome, caminho="/manga/naruto")
        
        cap1 = Capitulo(
            manga_nome=manga_nome,
            numero=1,
            nome_arquivo="cap1.pdf",
            caminho_completo="/manga/naruto/cap1.pdf"
        )
        
        cap2 = Capitulo(
            manga_nome=manga_nome,
            numero=2,
            nome_arquivo="cap2.pdf",
            caminho_completo="/manga/naruto/cap2.pdf"
        )
        
        assert cap1.manga_nome == manga.nome
        assert cap2.manga_nome == manga.nome
        assert cap1.numero == 1
        assert cap2.numero == 2

