"""
ReadsRepository — persiste estado de leitura em JSON
"""
import json
import os
from pathlib import Path


class ReadsRepository:
    def __init__(self, json_path: str):
        self.path = Path(json_path)
        self._ensure_file()

    def _ensure_file(self):
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text('{}', encoding='utf-8')

    def _load(self) -> dict:
        try:
            return json.loads(self.path.read_text(encoding='utf-8'))
        except Exception:
            return {}

    def _save(self, data: dict):
        self.path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

    def is_read(self, manga: str, filename: str) -> bool:
        data = self._load()
        return filename in data.get(manga, [])

    def get_reads(self, manga: str) -> list:
        return self._load().get(manga, [])

    def toggle(self, manga: str, filename: str) -> bool:
        """Alterna o estado. Retorna True se ficou marcado como lido."""
        data = self._load()
        reads = set(data.get(manga, []))
        if filename in reads:
            reads.discard(filename)
            is_read = False
        else:
            reads.add(filename)
            is_read = True
        data[manga] = list(reads)
        self._save(data)
        return is_read
