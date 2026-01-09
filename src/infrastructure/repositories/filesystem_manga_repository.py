"""
FileSystem Manga Repository - Implementação de repositório de mangás usando filesystem
"""
import os
from typing import List, Optional
from datetime import datetime

from ...domain.entities import Manga
from ...domain.repositories import IMangaRepository


class FileSystemMangaRepository(IMangaRepository):
    """
    Repositório de mangás que usa o sistema de arquivos.
    
    Estrutura esperada:
    base_dir/
    ├── Manga1/
    │   ├── capa.jpg (opcional)
    │   └── capitulo_XXX.pdf
    └── Manga2/
        └── capitulo_XXX.pdf
    """
    
    def __init__(self, base_dir: str):
        """
        Args:
            base_dir: Diretório base dos mangás (ex: ~/Comics)
        """
        self.base_dir = os.path.expanduser(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)
    
    def listar_todos(self) -> List[Manga]:
        """Retorna todos os mangás da biblioteca"""
        mangas = []
        
        if not os.path.exists(self.base_dir):
            return mangas
        
        for item in os.listdir(self.base_dir):
            caminho_completo = os.path.join(self.base_dir, item)
            
            # Só considera diretórios
            if os.path.isdir(caminho_completo):
                manga = self._criar_manga_de_diretorio(item, caminho_completo)
                mangas.append(manga)
        
        return sorted(mangas, key=lambda m: m.nome.lower())
    
    def buscar_por_nome(self, nome: str) -> Optional[Manga]:
        """Busca um mangá pelo nome"""
        caminho_manga = os.path.join(self.base_dir, nome)
        
        if not os.path.exists(caminho_manga) or not os.path.isdir(caminho_manga):
            return None
        
        return self._criar_manga_de_diretorio(nome, caminho_manga)
    
    def salvar(self, manga: Manga) -> Manga:
        """
        Salva ou atualiza um mangá.
        
        Note: Este método cria o diretório se não existir.
        """
        caminho_manga = os.path.join(self.base_dir, manga.nome)
        os.makedirs(caminho_manga, exist_ok=True)
        
        manga.caminho = caminho_manga
        
        return manga
    
    def deletar(self, nome: str) -> bool:
        """Deleta um mangá e todos seus capítulos"""
        caminho_manga = os.path.join(self.base_dir, nome)
        
        if not os.path.exists(caminho_manga):
            return False
        
        try:
            import shutil
            shutil.rmtree(caminho_manga)
            return True
        except Exception as e:
            print(f"Erro ao deletar mangá {nome}: {e}")
            return False
    
    def existe(self, nome: str) -> bool:
        """Verifica se um mangá existe"""
        caminho_manga = os.path.join(self.base_dir, nome)
        return os.path.exists(caminho_manga) and os.path.isdir(caminho_manga)
    
    def _criar_manga_de_diretorio(self, nome: str, caminho: str) -> Manga:
        """
        Cria entidade Manga a partir de um diretório.
        """
        # Verifica se tem capa
        capa_path = os.path.join(caminho, 'capa.jpg')
        tem_capa = os.path.exists(capa_path)
        capa_url = f"manga/{nome}/capa.jpg" if tem_capa else None
        
        # Conta capítulos (arquivos .pdf)
        total_capitulos = 0
        try:
            total_capitulos = len([
                f for f in os.listdir(caminho) 
                if f.lower().endswith('.pdf')
            ])
        except Exception:
            pass
        
        # Data de criação (do diretório)
        try:
            stat = os.stat(caminho)
            data_criacao = datetime.fromtimestamp(stat.st_ctime)
        except Exception:
            data_criacao = None
        
        return Manga(
            nome=nome,
            caminho=caminho,
            capa_url=capa_url,
            tem_capa=tem_capa,
            data_criacao=data_criacao,
            total_capitulos=total_capitulos
        )