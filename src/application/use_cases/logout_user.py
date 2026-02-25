from src.infrastructure.repositories.user_repository import UserRepository

class LogoutUserUseCase:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def execute(self, refresh_token: str):
        self.repo.revoke_refresh_token(refresh_token)
