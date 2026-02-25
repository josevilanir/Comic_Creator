"""
LogoutUserUseCase — Revogação de refresh token
"""
from src.infrastructure.repositories.sqlite_user_repository import SQLiteUserRepository


class LogoutUserUseCase:
    def __init__(self, user_repo: SQLiteUserRepository):
        self.user_repo = user_repo

    def executar(self, refresh_token: str):
        if refresh_token:
            self.user_repo.revogar_refresh_token(refresh_token)
