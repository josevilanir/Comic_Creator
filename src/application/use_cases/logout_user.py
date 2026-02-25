from src.infrastructure.repositories.sqlite_user_repository import SQLiteUserRepository as UserRepository

class LogoutUserUseCase:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def execute(self, refresh_token: str):
        self.repo.revoke_refresh_token(refresh_token)
