"""
S3CapituloRepository — ICapituloRepository backed by S3/R2.

salvar() faz upload do PDF e do thumbnail (se existir) do path local
informado em capitulo.caminho_completo para o S3.
"""
from __future__ import annotations
import os
import re
from typing import List, Optional

from src.domain.entities import Capitulo
from src.domain.repositories import ICapituloRepository
from src.infrastructure.services.s3_service import S3Service


class S3CapituloRepository(ICapituloRepository):
    def __init__(self, s3: S3Service):
        self.s3 = s3

    # ── helpers ────────────────────────────────────────────────────────────────

    def _manga_prefix(self, user_id: int, manga_nome: str) -> str:
        return f"user_{user_id}/{manga_nome}/"

    def _pdf_key(self, user_id: int, manga_nome: str, nome_arquivo: str) -> str:
        return f"user_{user_id}/{manga_nome}/{nome_arquivo}"

    def _thumb_key(self, user_id: int, manga_nome: str, nome_arquivo: str) -> str:
        return f"user_{user_id}/{manga_nome}/{nome_arquivo.replace('.pdf', '.jpg')}"

    def _extrair_numero(self, nome: str) -> int:
        m = re.search(r"(\d+)", nome)
        return int(m.group(1)) if m else 0

    # ── ICapituloRepository ────────────────────────────────────────────────────

    def listar_por_manga(self, user_id: int, manga_nome: str, ordem: str = "asc") -> List[Capitulo]:
        prefix = self._manga_prefix(user_id, manga_nome)
        objects = self.s3.list_objects(prefix)

        all_keys = {o["Key"] for o in objects}
        pdf_objects = [o for o in objects if o["Key"].endswith(".pdf")]

        capitulos = []
        for obj in pdf_objects:
            key = obj["Key"]
            nome_arquivo = key.split("/")[-1]
            thumb_key = key.replace(".pdf", ".jpg")
            capitulos.append(Capitulo(
                numero=self._extrair_numero(nome_arquivo),
                nome_arquivo=nome_arquivo,
                manga_nome=manga_nome,
                caminho_completo=key,
                thumbnail_url=thumb_key if thumb_key in all_keys else None,
            ))

        capitulos.sort(key=lambda c: c.numero, reverse=(ordem == "desc"))
        return capitulos

    def buscar(self, user_id: int, manga_nome: str, numero: int) -> Optional[Capitulo]:
        for cap in self.listar_por_manga(user_id, manga_nome):
            if cap.numero == numero:
                return cap
        return None

    def salvar(self, user_id: int, capitulo: Capitulo) -> Capitulo:
        """Faz upload do PDF (e thumbnail, se existir) para o S3."""
        pdf_key = self._pdf_key(user_id, capitulo.manga_nome, capitulo.nome_arquivo)
        self.s3.upload_file(capitulo.caminho_completo, pdf_key, "application/pdf")

        local_thumb = capitulo.caminho_completo.replace(".pdf", ".jpg")
        if os.path.exists(local_thumb):
            thumb_key = self._thumb_key(user_id, capitulo.manga_nome, capitulo.nome_arquivo)
            self.s3.upload_file(local_thumb, thumb_key, "image/jpeg")
            capitulo.thumbnail_url = thumb_key

        capitulo.caminho_completo = pdf_key
        return capitulo

    def deletar(self, user_id: int, manga_nome: str, nome_arquivo: str) -> bool:
        self.s3.delete_object(self._pdf_key(user_id, manga_nome, nome_arquivo))
        thumb_key = self._thumb_key(user_id, manga_nome, nome_arquivo)
        if self.s3.object_exists(thumb_key):
            self.s3.delete_object(thumb_key)
        return True

    def existe(self, user_id: int, manga_nome: str, numero: int) -> bool:
        return self.buscar(user_id, manga_nome, numero) is not None

    def contar_por_manga(self, user_id: int, manga_nome: str) -> int:
        return len(self.listar_por_manga(user_id, manga_nome))
