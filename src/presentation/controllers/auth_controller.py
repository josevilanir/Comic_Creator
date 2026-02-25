from flask import Blueprint, request, jsonify
from src.infrastructure.repositories.user_repository import UserRepository
from src.infrastructure.auth.jwt_service import JwtService
from src.application.use_cases.register_user import RegisterUserUseCase
from src.application.use_cases.login_user import LoginUserUseCase
from src.application.use_cases.refresh_token import RefreshTokenUseCase
from src.application.use_cases.logout_user import LogoutUserUseCase

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

repo = UserRepository()
jwt_svc = JwtService()

# Garantir tabelas ao importar
repo.create_tables()


@auth_bp.route("/register", methods=["POST"])
def register():
    body = request.get_json() or {}
    username = body.get("username", "").strip()
    email = body.get("email", "").strip()
    password = body.get("password", "")
    
    if not username or not email or not password:
        return jsonify({
            "status": "fail",
            "data": {"fields": "username, email e password são obrigatórios"}
        }), 400
    
    # Use cases agora lançam exceções de domínio que o centralized handler captura
    result = RegisterUserUseCase(repo, jwt_svc).execute(username, email, password)
    return jsonify({"status": "success", "data": result}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    body = request.get_json() or {}
    username = body.get("username", "").strip()
    password = body.get("password", "")
    
    if not username or not password:
        return jsonify({
            "status": "fail",
            "data": {"fields": "username e password são obrigatórios"}
        }), 400
    
    result = LoginUserUseCase(repo, jwt_svc).execute(username, password)
    return jsonify({"status": "success", "data": result}), 200


@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    body = request.get_json() or {}
    refresh_token = body.get("refresh_token", "")
    
    if not refresh_token:
        return jsonify({
            "status": "fail",
            "data": {"message": "refresh_token é obrigatório"}
        }), 400
    
    result = RefreshTokenUseCase(repo, jwt_svc).execute(refresh_token)
    return jsonify({"status": "success", "data": result}), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    body = request.get_json() or {}
    refresh_token = body.get("refresh_token", "")
    
    if refresh_token:
        LogoutUserUseCase(repo).execute(refresh_token)
    
    return jsonify({"status": "success", "data": {"message": "Logout realizado"}}), 200


@auth_bp.route("/me", methods=["GET"])
def me():
    """Endpoint de teste para verificar token"""
    from src.presentation.decorators.auth_required import auth_required
    from flask import g
    
    @auth_required
    def _me():
        return jsonify({"status": "success", "data": {"user_id": g.user_id, "username": g.username}}), 200
    
    return _me()
