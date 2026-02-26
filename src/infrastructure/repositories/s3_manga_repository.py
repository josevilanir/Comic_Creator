"""
S3MangaRepository — IMangaRepository backed by S3/R2 object storage.

Estrutura de keys:
    user_{id}/{manga_name}/capa.jpg
    user_{id}/{manga_name}/capitulo_001.pdf
    user_{id}/{manga_name}/capitulo_001.jpg   ← thumbnail

Mangás são "diretórios" implícitos no S3 (não existem de fato).
A lista de mangás é obtida agrupando todos os objetos do usuário por
prefixo — uma única operação de list com paginação.
"""
from __future__ import annotations
from typing import List, Optional

from src.domain.entities import Manga
from src.domain.repositories import IMangaRepository
from src.infrastructure.services.s3_service import S3Service


class S3MangaRepository(IMangaRepository):
    def __init__(self, s3: S3Service):
        self.s3 = s3

    # ── helpers ────────────────────────────────────────────────────────────────

    def _user_prefix(self, user_id: int) -> str:
        return f"user_{user_id}/"

    def _manga_prefix(self, user_id: int, nome: str) -> str:
        return f"user_{user_id}/{nome}/"

    # ── IMangaRepository ───────────────────────────────────────────────────────

    def listar_todos(self, user_id: int) -> List[Manga]:
        """Lista todos os mangás do usuário em uma única chamada ao S3."""
        prefix = self._user_prefix(user_id)
        all_objects = self.s3.list_objects(prefix)

        # Agrega objetos por nome do mangá
        manga_data: dict[str, dict] = {}
        for obj in all_objects:
            # key: user_{id}/{manga_name}/filename
            tail = obj["Key"][len(prefix):]       # {manga_name}/filename
            parts = tail.split("/", 1)
            if len(parts) < 2 or not parts[1]:    # ignora objects sem subpath
                continue

            manga_nome, filename = parts
            if manga_nome not in manga_data:
                manga_data[manga_nome] = {"pdfs": 0, "tem_capa": False, "capa_key": None}

            if filename.endswith(".pdf"):
                manga_data[manga_nome]["pdfs"] += 1
            elif filename == "capa.jpg":
                manga_data[manga_nome]["tem_capa"] = True
                manga_data[manga_nome]["capa_key"] = obj["Key"]

        result = []
        for nome, info in manga_data.items():
            result.append(Manga(
                nome=nome,
                caminho=self._manga_prefix(user_id, nome),
                tem_capa=info["tem_capa"],
                capa_url=info["capa_key"],
                total_capitulos=info["pdfs"],
            ))

        return sorted(result, key=lambda m: m.nome.lower())

    def buscar_por_nome(self, user_id: int, nome: str) -> Optional[Manga]:
        prefix = self._manga_prefix(user_id, nome)
        objects = self.s3.list_objects(prefix)
        if not objects:
            return None

        tem_capa = any(o["Key"].endswith("/capa.jpg") for o in objects)
        capa_key = next((o["Key"] for o in objects if o["Key"].endswith("/capa.jpg")), None)
        total_pdfs = sum(1 for o in objects if o["Key"].endswith(".pdf"))

        return Manga(
            nome=nome,
            caminho=prefix,
            tem_capa=tem_capa,
            capa_url=capa_key,
            total_capitulos=total_pdfs,
        )

    def salvar(self, user_id: int, manga: Manga) -> Manga:
        """No S3 não há 'diretórios' — apenas define o caminho lógico."""
        manga.caminho = self._manga_prefix(user_id, manga.nome)
        return manga

    def deletar(self, user_id: int, nome: str) -> bool:
        prefix = self._manga_prefix(user_id, nome)
        self.s3.delete_prefix(prefix)
        return True

    def existe(self, user_id: int, nome: str) -> bool:
        prefix = self._manga_prefix(user_id, nome)
        return bool(self.s3.list_objects(prefix))
