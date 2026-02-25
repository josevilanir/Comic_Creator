"""
FileSystem Manga Repository - Implementação de repositório de mangás usando filesystem isolado por usuário
"""
import os
from typing import List, Optional
from datetime import datetime

from ...domain.entities import Manga
from ...domain.repositories import IMangaRepository


class FileSystemMangaRepository(IMangaRepository):
    """
    Repositório de mangás que usa o sistema de arquivos isolado por usuário.
    Estrutura: base_dir/user_{id}/MangaName/...
    """
    
    def __init__(self, base_dir: str):
        self.base_dir = os.path.expanduser(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_user_path(self, user_id: int) -> str:
        path = os.path.join(self.base_dir, f"user_{user_id}")
        os.makedirs(path, exist_ok=True)
        return path
    
    def listar_todos(self, user_id: int) -> List[Manga]:
        mangas = []
        user_path = self._get_user_path(user_id)
        
        for item in os.listdir(user_path):
            caminho_completo = os.path.join(user_path, item)
            if os.path.isdir(caminho_completo):
                manga = self._criar_manga_de_diretorio(item, caminho_completo)
                mangas.append(manga)
        
        return sorted(mangas, key=lambda m: m.nome.lower())
    
    def buscar_por_nome(self, user_id: int, nome: str) -> Optional[Manga]:
        user_path = self._get_user_path(user_id)
        caminho_manga = os.path.join(user_path, nome)
        
        if not os.path.exists(caminho_manga) or not os.path.isdir(caminho_manga):
            return None
        
        return self._criar_manga_de_diretorio(nome, caminho_manga)
    
    def salvar(self, user_id: int, manga: Manga) -> Manga:
        user_path = self._get_user_path(user_id)
        caminho_manga = os.path.join(user_path, manga.nome)
        os.makedirs(caminho_manga, exist_ok=True)
        manga.caminho = caminho_manga
        return manga
    
    def deletar(self, user_id: int, nome: str) -> bool:
        user_path = self._get_user_path(user_id)
        caminho_manga = os.path.join(user_path, nome)
        
        if not os.path.exists(caminho_manga):
            return False
        
        try:
            import shutil
            shutil.rmtree(caminho_manga)
            return True
        except Exception:
            return False
    
    def existe(self, user_id: int, nome: str) -> bool:
        user_path = self._get_user_path(user_id)
        caminho_manga = os.path.join(user_path, nome)
        return os.path.exists(caminho_manga) and os.path.isdir(caminho_manga)
    
    def _criar_manga_de_diretorio(self, nome: str, caminho: str) -> Manga:
        capa_path = os.path.join(caminho, 'capa.jpg')
        tem_capa = os.path.exists(capa_path)
        capa_url = f"manga/{nome}/capa.jpg" if tem_capa else None
        
        total_capitulos = 0
        try:
            total_capitulos = len([
                f for f in os.listdir(caminho) 
                if f.lower().endswith('.pdf')
            ])
        except Exception: pass
        
        try:
            stat = os.stat(caminho)
            data_criacao = datetime.fromtimestamp(stat.st_ctime)
        except Exception: data_criacao = None
        
        return Manga(
            nome=nome,
            caminho=caminho,
            capa_url=capa_url,
            tem_capa=tem_capa,
            data_criacao=data_criacao,
            total_capitulos=total_capitulos
        )
