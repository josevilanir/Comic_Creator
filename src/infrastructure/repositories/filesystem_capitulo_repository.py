"""
FileSystem Capitulo Repository - Implementação de repositório de capítulos usando filesystem isolado por usuário
"""
import os
import re
import shutil
from typing import List, Optional
from ...domain.entities import Capitulo
from ...domain.repositories import ICapituloRepository


class FileSystemCapituloRepository(ICapituloRepository):
    def __init__(self, base_dir: str):
        self.base_dir = os.path.expanduser(base_dir)

    def _get_manga_path(self, user_id: int, manga_nome: str) -> str:
        return os.path.join(self.base_dir, f"user_{user_id}", manga_nome)

    def _extrair_numero(self, nome: str) -> int:
        match = re.search(r'(\d+)', nome)
        return int(match.group(1)) if match else 0

    def listar_por_manga(self, user_id: int, manga_nome: str, ordem: str = 'asc') -> List[Capitulo]:
        capitulos = []
        manga_path = self._get_manga_path(user_id, manga_nome)
        
        if not os.path.exists(manga_path):
            return capitulos
            
        for f in os.listdir(manga_path):
            if f.lower().endswith('.pdf'):
                capitulos.append(Capitulo(
                    numero=self._extrair_numero(f),
                    nome_arquivo=f,
                    manga_nome=manga_nome,
                    caminho_completo=os.path.join(manga_path, f)
                ))
        
        capitulos.sort(key=lambda c: c.numero, reverse=(ordem == 'desc'))
        return capitulos

    def buscar(self, user_id: int, manga_nome: str, numero: int) -> Optional[Capitulo]:
        for cap in self.listar_por_manga(user_id, manga_nome):
            if cap.numero == numero:
                return cap
        return None

    def salvar(self, user_id: int, capitulo: Capitulo) -> Capitulo:
        manga_path = self._get_manga_path(user_id, capitulo.manga_nome)
        os.makedirs(manga_path, exist_ok=True)

        dest_pdf = os.path.join(manga_path, capitulo.nome_arquivo)
        if capitulo.caminho_completo != dest_pdf:
            shutil.copy2(capitulo.caminho_completo, dest_pdf)

        # Copia thumbnail se existir junto ao PDF na pasta temp
        src_thumb = capitulo.caminho_completo.replace(".pdf", ".jpg")
        dest_thumb = os.path.join(manga_path, capitulo.nome_arquivo.replace(".pdf", ".jpg"))
        if os.path.exists(src_thumb) and src_thumb != dest_thumb:
            shutil.copy2(src_thumb, dest_thumb)

        capitulo.caminho_completo = dest_pdf
        return capitulo

    def deletar(self, user_id: int, manga_nome: str, nome_arquivo: str) -> bool:
        manga_path = self._get_manga_path(user_id, manga_nome)
        caminho = os.path.join(manga_path, nome_arquivo)
        
        if not os.path.exists(caminho):
            return False
            
        try:
            os.remove(caminho)
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
