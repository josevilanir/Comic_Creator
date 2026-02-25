from flask import Blueprint, request, jsonify, current_app
from src.infrastructure.auth.jwt_service import JwtService
from src.application.use_cases.register_user import RegisterUserUseCase
from src.application.use_cases.login_user import LoginUserUseCase
from src.application.use_cases.refresh_token import RefreshTokenUseCase
from src.application.use_cases.logout_user import LogoutUserUseCase

auth_bp = Blueprint("auth", __name__)

jwt_svc = JwtService()

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
    
    try:
        container = current_app.container
        result = RegisterUserUseCase(container.user_repository, jwt_svc).execute(username, email, password)
        return jsonify({"status": "success", "data": result}), 201
    except Exception as e:
        return jsonify({"status": "fail", "data": {"message": str(e)}}), 409


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
    
    try:
        container = current_app.container
        result = LoginUserUseCase(container.user_repository, jwt_svc).execute(username, password)
        return jsonify({"status": "success", "data": result}), 200
    except Exception as e:
        return jsonify({"status": "fail", "data": {"message": str(e)}}), 401


@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    body = request.get_json() or {}
    refresh_token = body.get("refresh_token", "")
    
    if not refresh_token:
        return jsonify({
            "status": "fail",
            "data": {"message": "refresh_token é obrigatório"}
        }), 400
    
    try:
        container = current_app.container
        result = RefreshTokenUseCase(container.user_repository, jwt_svc).execute(refresh_token)
        return jsonify({"status": "success", "data": result}), 200
    except Exception as e:
        return jsonify({"status": "fail", "data": {"message": str(e)}}), 401


@auth_bp.route("/logout", methods=["POST"])
def logout():
    body = request.get_json() or {}
    refresh_token = body.get("refresh_token", "")
    
    if refresh_token:
        container = current_app.container
        LogoutUserUseCase(container.user_repository).execute(refresh_token)
    
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
