from src.infrastructure.repositories.sqlite_user_repository import SQLiteUserRepository as UserRepository
from src.infrastructure.auth.jwt_service import JwtService
from src.domain.exceptions import UserAlreadyExistsException, ValidationException

class RegisterUserUseCase:
    def __init__(self, repo: UserRepository, jwt: JwtService):
        self.repo = repo
        self.jwt = jwt

    def execute(self, username: str, email: str, password: str) -> dict:
        if len(password) < 6:
            raise ValidationException("Senha deve ter pelo menos 6 caracteres", field="password")
        if self.repo.find_by_username(username):
            raise UserAlreadyExistsException(username)
        if self.repo.find_by_email(email):
            raise UserAlreadyExistsException(email) # Ou uma exceção mais específica para email
        
        from src.domain.entities.user import User
        password_hash = self.jwt.hash_password(password)
        user = User(id=None, username=username, email=email, password_hash=password_hash)
        user = self.repo.create(user)
        
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
