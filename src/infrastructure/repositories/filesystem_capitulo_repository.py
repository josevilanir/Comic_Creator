"""
FileSystem Capitulo Repository - Implementação de repositório de capítulos
"""
import os
from typing import List, Optional
from datetime import datetime

from ...domain.entities import Capitulo
from ...domain.repositories import ICapituloRepository


class FileSystemCapituloRepository(ICapituloRepository):
    """
    Repositório de capítulos que usa o sistema de arquivos.
    
    Estrutura esperada:
    base_dir/
    └── MangaX/
        ├── capitulo_001.pdf
        ├── capitulo_001.jpg (thumbnail)
        ├── capitulo_002.pdf
        └── capitulo_002.jpg
    """
    
    def __init__(self, base_dir: str):
        """
        Args:
            base_dir: Diretório base dos mangás
        """
        self.base_dir = os.path.expanduser(base_dir)
    
    def listar_por_manga(self, manga_nome: str, ordem: str = 'asc') -> List[Capitulo]:
        """
        Lista todos os capítulos de um mangá.
        
        Args:
            manga_nome: Nome do mangá
            ordem: 'asc' ou 'desc'
            
        Returns:
            Lista de capítulos ordenados
        """
        pasta_manga = os.path.join(self.base_dir, manga_nome)
        
        if not os.path.exists(pasta_manga):
            return []
        
        # Lista arquivos PDF
        try:
            arquivos_pdf = [
                f for f in os.listdir(pasta_manga) 
                if f.lower().endswith('.pdf')
            ]
        except Exception:
            return []
        
        # Ordena numericamente pelo número do capítulo
        try:
            arquivos_ordenados = sorted(
                arquivos_pdf,
                key=lambda nome: int(''.join(filter(str.isdigit, os.path.splitext(nome)[0])) or 0),
                reverse=(ordem == 'desc')
            )
        except ValueError:
            # Se falhar ordenação numérica, usa alfabética
            arquivos_ordenados = sorted(arquivos_pdf, reverse=(ordem == 'desc'))
        
        # Cria entidades Capitulo
        capitulos = []
        for arquivo in arquivos_ordenados:
            capitulo = self._criar_capitulo_de_arquivo(manga_nome, arquivo, pasta_manga)
            if capitulo:
                capitulos.append(capitulo)
        
        return capitulos
    
    def buscar(self, manga_nome: str, numero: int) -> Optional[Capitulo]:
        """
        Busca um capítulo específico.
        
        Args:
            manga_nome: Nome do mangá
            numero: Número do capítulo
            
        Returns:
            Capitulo ou None
        """
        pasta_manga = os.path.join(self.base_dir, manga_nome)
        
        if not os.path.exists(pasta_manga):
            return None
        
        # Procura arquivo que corresponde ao número
        nome_esperado = f"capitulo_{str(numero).zfill(3)}.pdf"
        caminho_arquivo = os.path.join(pasta_manga, nome_esperado)
        
        if os.path.exists(caminho_arquivo):
            return self._criar_capitulo_de_arquivo(manga_nome, nome_esperado, pasta_manga)
        
        # Busca alternativa por número (caso formato seja diferente)
        try:
            arquivos = os.listdir(pasta_manga)
            for arquivo in arquivos:
                if arquivo.lower().endswith('.pdf'):
                    # Extrai número do arquivo
                    numeros = ''.join(filter(str.isdigit, os.path.splitext(arquivo)[0]))
                    if numeros and int(numeros) == numero:
                        return self._criar_capitulo_de_arquivo(manga_nome, arquivo, pasta_manga)
        except Exception:
            pass
        
        return None
    
    def salvar(self, capitulo: Capitulo) -> Capitulo:
        """
        Salva um capítulo.
        
        Note: Assume que arquivo PDF já existe no caminho_completo.
        """
        # Verifica se arquivo existe
        if not os.path.exists(capitulo.caminho_completo):
            raise FileNotFoundError(f"Arquivo não encontrado: {capitulo.caminho_completo}")
        
        # Atualiza tamanho
        capitulo.tamanho_bytes = os.path.getsize(capitulo.caminho_completo)
        
        return capitulo
    
    def deletar(self, manga_nome: str, nome_arquivo: str) -> bool:
        """
        Deleta um capítulo específico.
        
        Args:
            manga_nome: Nome do mangá
            nome_arquivo: Nome do arquivo PDF
            
        Returns:
            True se deletou
        """
        pasta_manga = os.path.join(self.base_dir, manga_nome)
        caminho_pdf = os.path.join(pasta_manga, nome_arquivo)
        
        if not os.path.exists(caminho_pdf):
            return False
        
        try:
            # Deleta PDF
            os.remove(caminho_pdf)
            
            # Deleta thumbnail se existir
            nome_thumb = nome_arquivo.replace('.pdf', '.jpg')
            caminho_thumb = os.path.join(pasta_manga, nome_thumb)
            if os.path.exists(caminho_thumb):
                os.remove(caminho_thumb)
            
            return True
            
        except Exception as e:
            print(f"Erro ao deletar capítulo: {e}")
            return False
    
    def existe(self, manga_nome: str, numero: int) -> bool:
        """Verifica se um capítulo existe"""
        return self.buscar(manga_nome, numero) is not None
    
    def contar_por_manga(self, manga_nome: str) -> int:
        """Conta quantos capítulos um mangá possui"""
        pasta_manga = os.path.join(self.base_dir, manga_nome)
        
        if not os.path.exists(pasta_manga):
            return 0
        
        try:
            return len([
                f for f in os.listdir(pasta_manga) 
                if f.lower().endswith('.pdf')
            ])
        except Exception:
            return 0
    
    def _criar_capitulo_de_arquivo(
        self, 
        manga_nome: str, 
        nome_arquivo: str,
        pasta_manga: str
    ) -> Optional[Capitulo]:
        """
        Cria entidade Capitulo a partir de arquivo.
        """
        # Extrai número do capítulo
        try:
            numeros = ''.join(filter(str.isdigit, os.path.splitext(nome_arquivo)[0]))
            numero = int(numeros) if numeros else 0
        except ValueError:
            numero = 0
        
        caminho_completo = os.path.join(pasta_manga, nome_arquivo)
        
        # Verifica thumbnail
        nome_thumb = nome_arquivo.replace('.pdf', '.jpg')
        caminho_thumb = os.path.join(pasta_manga, nome_thumb)
        thumbnail_url = f"manga/{manga_nome}/{nome_thumb}" if os.path.exists(caminho_thumb) else None
        
        # Tamanho do arquivo
        try:
            tamanho_bytes = os.path.getsize(caminho_completo)
        except Exception:
            tamanho_bytes = None
        
        # Data de download (data de criação do arquivo)
        try:
            stat = os.stat(caminho_completo)
            data_download = datetime.fromtimestamp(stat.st_ctime)
        except Exception:
            data_download = None
        
        try:
            return Capitulo(
                numero=numero,
                nome_arquivo=nome_arquivo,
                manga_nome=manga_nome,
                caminho_completo=caminho_completo,
                thumbnail_url=thumbnail_url,
                lido=False,  # Status de leitura virá de outra fonte
                data_download=data_download,
                tamanho_bytes=tamanho_bytes
            )
        except ValueError as e:
            print(f"Erro ao criar capitulo {nome_arquivo}: {e}")
            return None