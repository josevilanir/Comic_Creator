from src.infrastructure.repositories.user_repository import UserRepository
from src.infrastructure.auth.jwt_service import JwtService
from src.domain.exceptions import InvalidCredentialsException

class LoginUserUseCase:
    def __init__(self, repo: UserRepository, jwt: JwtService):
        self.repo = repo
        self.jwt = jwt

    def execute(self, username: str, password: str) -> dict:
        user = self.repo.find_by_username(username)
        if not user or not self.jwt.verify_password(password, user.password_hash):
            raise InvalidCredentialsException()
        
        access_token = self.jwt.create_access_token(user.id, user.username)
        refresh_token = self.jwt.create_refresh_token(user.id)
        
        from datetime import datetime, timedelta, timezone
        expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        self.repo.save_refresh_token(user.id, refresh_token, expires_at)
        
        return {
            "user": {"id": user.id, "username": user.username, "email": user.email},
            "access_token": access_token,
            "refresh_token": refresh_token
        }
