"""
FileSystem Capitulo Repository - Implementação de repositório de capítulos usando filesystem isolado por usuário
"""
import os
from typing import List, Optional
from ...domain.entities import Capitulo
from ...domain.repositories import ICapituloRepository


class FileSystemCapituloRepository(ICapituloRepository):
    def __init__(self, base_dir: str):
        self.base_dir = os.path.expanduser(base_dir)

    def _get_manga_path(self, user_id: int, manga_nome: str) -> str:
        return os.path.join(self.base_dir, f"user_{user_id}", manga_nome)

    def listar_por_manga(self, user_id: int, manga_nome: str, ordem: str = 'asc') -> List[Capitulo]:
        capitulos = []
        manga_path = self._get_manga_path(user_id, manga_nome)
        
        if not os.path.exists(manga_path):
            return capitulos
            
        for f in os.listdir(manga_path):
            if f.lower().endswith('.pdf'):
                capitulos.append(Capitulo(
                    nome_manga=manga_nome,
                    nome_arquivo=f,
                    caminho_completo=os.path.join(manga_path, f),
                    tem_thumbnail=os.path.exists(os.path.join(manga_path, f.replace('.pdf', '.jpg')))
                ))
        
        # Ordenação natural por número no título
        import re
        def extrair_numero(nome):
            match = re.search(r'(\d+)', nome)
            return int(match.group(1)) if match else 0
            
        capitulos.sort(key=lambda c: extrair_numero(c.nome_arquivo), reverse=(ordem == 'desc'))
        return capitulos

    def buscar(self, user_id: int, manga_nome: str, numero: int) -> Optional[Capitulo]:
        # Implementação simplificada baseada no nome
        for cap in self.listar_por_manga(user_id, manga_nome):
            if f"capitulo_{numero:03d}" in cap.nome_arquivo or f"cap_{numero}" in cap.nome_arquivo:
                return cap
        return None

    def salvar(self, user_id: int, capitulo: Capitulo) -> Capitulo:
        # O use case de download já salva o arquivo no disco. 
        # O repositório apenas garante que o objeto retornado tenha os caminhos corretos.
        manga_path = self._get_manga_path(user_id, capitulo.nome_manga)
        capitulo.caminho_completo = os.path.join(manga_path, capitulo.nome_arquivo)
        return capitulo

    def deletar(self, user_id: int, manga_nome: str, nome_arquivo: str) -> bool:
        manga_path = self._get_manga_path(user_id, manga_nome)
        caminho = os.path.join(manga_path, nome_arquivo)
        
        if not os.path.exists(caminho):
            return False
            
        try:
            os.remove(caminho)
            # Remove thumbnail se existir
            thumb = caminho.replace('.pdf', '.jpg')
            if os.path.exists(thumb):
                os.remove(thumb)
            return True
        except Exception:
            return False

    def existe(self, user_id: int, manga_nome: str, numero: int) -> bool:
        return self.buscar(user_id, manga_nome, numero) is not None

    def contar_por_manga(self, user_id: int, manga_nome: str) -> int:
        return len(self.listar_por_manga(user_id, manga_nome))
