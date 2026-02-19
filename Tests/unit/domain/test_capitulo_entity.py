"""
Testes unitários para entidade Capitulo
"""
import pytest
from datetime import datetime
from src.domain.entities.capitulo import Capitulo


@pytest.mark.unit
class TestCapituloEntity:
    """Testes da entidade Capitulo"""
    
    def test_criar_capitulo_valido(self):
        """Deve criar capítulo com dados válidos"""
        cap = Capitulo(
            manga_nome="One Piece",
            numero=1,
            nome_arquivo="Capitulo_1.pdf",
            caminho_completo="/tmp/one_piece/cap_1.pdf",
            lido=False
        )
        
        assert cap.manga_nome == "One Piece"
        assert cap.numero == 1
        assert cap.nome_arquivo == "Capitulo_1.pdf"
        assert cap.caminho_completo == "/tmp/one_piece/cap_1.pdf"
        assert cap.lido is False
    
    def test_numero_negativo_deve_falhar(self):
        """Não deve aceitar número negativo"""
        with pytest.raises(ValueError, match="Número do capítulo deve ser positivo"):
            Capitulo(
                manga_nome="Test",
                numero=-1,
                nome_arquivo="test.pdf",
                caminho_completo="/tmp/test.pdf"
            )
    
    def test_arquivo_sem_extensao_pdf_deve_falhar(self):
        """Não deve aceitar arquivo sem extensão .pdf"""
        with pytest.raises(ValueError, match="Nome do arquivo deve ter extensão .pdf"):
            Capitulo(
                manga_nome="Test",
                numero=1,
                nome_arquivo="test.txt",
                caminho_completo="/tmp/test.txt"
            )
    
    def test_manga_nome_vazio_deve_falhar(self):
        """Não deve aceitar manga_nome vazio"""
        with pytest.raises(ValueError, match="Capítulo deve pertencer a um mangá"):
            Capitulo(
                manga_nome="",
                numero=1,
                nome_arquivo="test.pdf",
                caminho_completo="/tmp/test.pdf"
            )
    
    def test_marcar_como_lido(self):
        """Deve marcar capítulo como lido"""
        cap = Capitulo(
            manga_nome="Test",
            numero=1,
            nome_arquivo="test.pdf",
            caminho_completo="/tmp/test.pdf",
            lido=False
        )
        
        assert cap.lido is False
        
        cap.marcar_como_lido()
        
        assert cap.lido is True
    
    def test_capitulo_numero_zero_permitido(self):
        """Número zero deve ser permitido (representa capítulo especial ou inicial)"""
        cap = Capitulo(
            manga_nome="Test",
            numero=0,
            nome_arquivo="special.pdf",
            caminho_completo="/tmp/special.pdf"
        )
        
        assert cap.numero == 0
    
    def test_capitulo_com_dados_opcionais(self):
        """Deve aceitar dados opcionais corretamente"""
        agora = datetime.now()
        cap = Capitulo(
            manga_nome="Test",
            numero=1,
            nome_arquivo="test.pdf",
            caminho_completo="/tmp/test.pdf",
            thumbnail_url="https://example.com/thumb.jpg",
            lido=True,
            data_download=agora,
            tamanho_bytes=1024000
        )
        
        assert cap.thumbnail_url == "https://example.com/thumb.jpg"
        assert cap.lido is True
        assert cap.data_download == agora
        assert cap.tamanho_bytes == 1024000
    
    def test_arquivo_multiplos_pontos_com_pdf_extensao(self):
        """Deve aceitar arquivo com múltiplos pontos se termina em .pdf"""
        cap = Capitulo(
            manga_nome="Test",
            numero=1,
            nome_arquivo="Capitulo.1-2024.pdf",
            caminho_completo="/tmp/Capitulo.1-2024.pdf"
        )
        
        assert cap.nome_arquivo == "Capitulo.1-2024.pdf"
