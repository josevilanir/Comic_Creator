"""
UserUserDataRepository — gerencia leituras e progresso de cada usuário no SQLite.
"""
import sqlite3
from typing import List, Set

class UserDataRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._create_tables()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_reads (
                    user_id INTEGER NOT NULL,
                    manga_name TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    PRIMARY KEY (user_id, manga_name, filename),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_progress (
                    user_id INTEGER NOT NULL,
                    manga_name TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    page INTEGER NOT NULL,
                    PRIMARY KEY (user_id, manga_name, filename),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

    # ─── Reads ───────────────────────────────────────────────────────────
    
    def toggle_read(self, user_id: int, manga_name: str, filename: str) -> bool:
        """Alterna estado de lido. Retorna o novo estado."""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT 1 FROM user_reads WHERE user_id = ? AND manga_name = ? AND filename = ?",
                (user_id, manga_name, filename)
            ).fetchone()
            
            if row:
                conn.execute(
                    "DELETE FROM user_reads WHERE user_id = ? AND manga_name = ? AND filename = ?",
                    (user_id, manga_name, filename)
                )
                return False
            else:
                conn.execute(
                    "INSERT INTO user_reads (user_id, manga_name, filename) VALUES (?, ?, ?)",
                    (user_id, manga_name, filename)
                )
                return True

    def get_reads(self, user_id: int, manga_name: str) -> Set[str]:
        """Retorna conjunto de filenames lidos por um usuário para um mangá."""
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT filename FROM user_reads WHERE user_id = ? AND manga_name = ?",
                (user_id, manga_name)
            ).fetchall()
        return {row["filename"] for row in rows}

    # ─── Progress ────────────────────────────────────────────────────────
    
    def get_progress(self, user_id: int, manga_name: str, filename: str) -> int:
        """Retorna a última página salva. Padrão: 1."""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT page FROM user_progress WHERE user_id = ? AND manga_name = ? AND filename = ?",
                (user_id, manga_name, filename)
            ).fetchone()
        return row["page"] if row else 1

    def save_progress(self, user_id: int, manga_name: str, filename: str, page: int):
        """Salva a página atual do usuário."""
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO user_progress (user_id, manga_name, filename, page)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, manga_name, filename) 
                DO UPDATE SET page = excluded.page
            """, (user_id, manga_name, filename, page))
