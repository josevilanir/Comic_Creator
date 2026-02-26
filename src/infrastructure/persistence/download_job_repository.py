"""
DownloadJobRepository — persiste jobs de download no SQLite.

Substitui o dict em memória que era perdido a cada reinicialização.
"""
import json
import sqlite3
from typing import Optional


class DownloadJobRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._create_table()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_table(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS download_jobs (
                    job_id      TEXT    PRIMARY KEY,
                    user_id     INTEGER NOT NULL,
                    status      TEXT    NOT NULL DEFAULT 'rodando',
                    total       INTEGER NOT NULL,
                    concluido   INTEGER NOT NULL DEFAULT 0,
                    atual       INTEGER,
                    resultados  TEXT    NOT NULL DEFAULT '[]',
                    cancelar    INTEGER NOT NULL DEFAULT 0,
                    created_at  TEXT    DEFAULT (datetime('now'))
                )
            """)

    # ── escrita ────────────────────────────────────────────────────────────────

    def criar(self, job_id: str, user_id: int, total: int) -> None:
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO download_jobs (job_id, user_id, total) VALUES (?, ?, ?)",
                (job_id, user_id, total),
            )

    def atualizar_atual(self, job_id: str, cap_num: int) -> None:
        with self._get_conn() as conn:
            conn.execute(
                "UPDATE download_jobs SET atual = ? WHERE job_id = ?",
                (cap_num, job_id),
            )

    def registrar_resultado(self, job_id: str, resultado: dict) -> None:
        """Adiciona resultado de um capítulo e incrementa o contador concluido."""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT resultados FROM download_jobs WHERE job_id = ?", (job_id,)
            ).fetchone()
            resultados = json.loads(row["resultados"]) if row else []
            resultados.append(resultado)
            conn.execute(
                "UPDATE download_jobs SET resultados = ?, concluido = concluido + 1 WHERE job_id = ?",
                (json.dumps(resultados), job_id),
            )

    def definir_status(self, job_id: str, status: str) -> None:
        with self._get_conn() as conn:
            conn.execute(
                "UPDATE download_jobs SET status = ?, atual = NULL WHERE job_id = ?",
                (status, job_id),
            )

    def solicitar_cancelamento(self, job_id: str, user_id: int) -> bool:
        with self._get_conn() as conn:
            cursor = conn.execute(
                "UPDATE download_jobs SET cancelar = 1 WHERE job_id = ? AND user_id = ?",
                (job_id, user_id),
            )
        return cursor.rowcount > 0

    # ── leitura ────────────────────────────────────────────────────────────────

    def buscar(self, job_id: str, user_id: int) -> Optional[dict]:
        """Retorna o job somente se pertencer ao user_id informado."""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM download_jobs WHERE job_id = ? AND user_id = ?",
                (job_id, user_id),
            ).fetchone()
        if not row:
            return None
        return {
            "status":     row["status"],
            "total":      row["total"],
            "concluido":  row["concluido"],
            "atual":      row["atual"],
            "resultados": json.loads(row["resultados"]),
            "cancelar":   bool(row["cancelar"]),
            "user_id":    row["user_id"],
        }

    def deve_cancelar(self, job_id: str) -> bool:
        """Verifica se cancelamento foi solicitado (chamado da thread)."""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT cancelar FROM download_jobs WHERE job_id = ?", (job_id,)
            ).fetchone()
        return bool(row["cancelar"]) if row else False
