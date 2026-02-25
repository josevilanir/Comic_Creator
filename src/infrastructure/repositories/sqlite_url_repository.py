"""
SQLite URL Repository - Implementação isolada por usuário
"""
import sqlite3
from typing import List, Optional
from ...domain.entities import URLSalva
from ...domain.repositories import IURLSalvaRepository


class SQLiteURLRepository(IURLSalvaRepository):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._create_table()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_table(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_urls (
                    user_id INTEGER NOT NULL,
                    manga_name TEXT NOT NULL,
                    url_base TEXT NOT NULL,
                    PRIMARY KEY (user_id, manga_name),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

    def listar_todas(self, user_id: int) -> List[URLSalva]:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM user_urls WHERE user_id = ? ORDER BY manga_name", (user_id,)
            ).fetchall()
        return [URLSalva(nome_manga=row["manga_name"], url_base=row["url_base"]) for row in rows]

    def buscar_por_nome(self, user_id: int, nome_manga: str) -> Optional[URLSalva]:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM user_urls WHERE user_id = ? AND manga_name = ?", (user_id, nome_manga)
            ).fetchone()
        if not row: return None
        return URLSalva(nome_manga=row["manga_name"], url_base=row["url_base"])

    def salvar(self, user_id: int, url: URLSalva) -> URLSalva:
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO user_urls (user_id, manga_name, url_base)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, manga_name) DO UPDATE SET url_base = excluded.url_base
            """, (user_id, url.nome_manga, url.url_base))
        return url

    def deletar(self, user_id: int, nome_manga: str) -> bool:
        with self._get_conn() as conn:
            cursor = conn.execute(
                "DELETE FROM user_urls WHERE user_id = ? AND manga_name = ?", (user_id, nome_manga)
            )
            return cursor.rowcount > 0

    def existe(self, user_id: int, nome_manga: str) -> bool:
        return self.buscar_por_nome(user_id, nome_manga) is not None
