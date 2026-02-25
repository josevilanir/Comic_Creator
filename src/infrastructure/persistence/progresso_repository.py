"""
ProgressoRepository — persiste progresso de leitura em JSON.
Formato do arquivo:
{
  "NomeManga": {
    "capitulo1.pdf": 7,
    "capitulo2.pdf": 1
  }
}
"""
import json
from pathlib import Path


class ProgressoRepository:
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

    def get_pagina(self, manga: str, filename: str) -> int:
        """Retorna a última página salva. Padrão: 1."""
        data = self._load()
        return data.get(manga, {}).get(filename, 1)

    def save_pagina(self, manga: str, filename: str, pagina: int) -> None:
        """Salva a página atual do usuário."""
        data = self._load()
        if manga not in data:
            data[manga] = {}
        data[manga][filename] = pagina
        self._save(data)

    def get_all(self, manga: str) -> dict:
        """Retorna todo o progresso de um mangá. Ex: { 'cap1.pdf': 7 }"""
        return self._load().get(manga, {})
