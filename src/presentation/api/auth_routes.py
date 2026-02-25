"""
Auth API Routes — Endpoints REST de autenticação (/api/v1/auth)
Blueprint separado do auth_controller.py (Jinja2/legado). Este é o REST/JSend.
"""
from flask import Blueprint, request, current_app
from src.presentation.api.jsend import success, fail, error
from src.application.use_cases import (
    RegisterUserUseCase,
    LoginUserUseCase,
    RefreshTokenUseCase,
    LogoutUserUseCase,
)

auth_api_bp = Blueprint('auth_api', __name__, url_prefix='/api/v1/auth')


def _get_use_cases(container):
    """Instancia os use cases injetando dependências do container."""
    return {
        'register': RegisterUserUseCase(container.user_repository, container.hash_service, container.jwt_service),
        'login':    LoginUserUseCase(container.user_repository, container.hash_service, container.jwt_service),
        'refresh':  RefreshTokenUseCase(container.user_repository, container.jwt_service),
        'logout':   LogoutUserUseCase(container.user_repository),
    }


@auth_api_bp.route('/register', methods=['POST'])
def register():
    body = request.get_json() or {}
    username = body.get('username', '').strip()
    password = body.get('password', '')

    if not username or not password:
        return fail({'fields': 'username e password são obrigatórios'})

    try:
        uc = _get_use_cases(current_app.container)
        result = uc['register'].executar(username, password)
        return success(result, 201)
    except ValueError as e:
        return fail({'message': str(e)}, 409)
    except Exception as e:
        current_app.logger.error(f'Erro no registro: {e}')
        return error('Erro interno no registro', 'REGISTER_ERROR')


@auth_api_bp.route('/login', methods=['POST'])
def login():
    body = request.get_json() or {}
    username = body.get('username', '').strip()
    password = body.get('password', '')

    if not username or not password:
        return fail({'fields': 'username e password são obrigatórios'})

    try:
        uc = _get_use_cases(current_app.container)
        result = uc['login'].executar(username, password)
        return success(result)
    except ValueError as e:
        return fail({'message': str(e)}, 401)
    except Exception as e:
        current_app.logger.error(f'Erro no login: {e}')
        return error('Erro interno no login', 'LOGIN_ERROR')


@auth_api_bp.route('/refresh', methods=['POST'])
def refresh():
    body = request.get_json() or {}
    refresh_token = body.get('refresh_token', '')

    if not refresh_token:
        return fail({'message': 'refresh_token é obrigatório'})

    try:
        uc = _get_use_cases(current_app.container)
        result = uc['refresh'].executar(refresh_token)
        return success(result)
    except ValueError as e:
        return fail({'message': str(e)}, 401)
    except Exception as e:
        current_app.logger.error(f'Erro no refresh: {e}')
        return error('Erro interno no refresh', 'REFRESH_ERROR')


@auth_api_bp.route('/logout', methods=['POST'])
def logout():
    body = request.get_json() or {}
    refresh_token = body.get('refresh_token', '')

    try:
        uc = _get_use_cases(current_app.container)
        uc['logout'].executar(refresh_token)
        return success({'message': 'Logout realizado com sucesso'})
    except Exception as e:
        current_app.logger.error(f'Erro no logout: {e}')
        return error('Erro interno no logout', 'LOGOUT_ERROR')


@auth_api_bp.route('/me', methods=['GET'])
def me():
    """Verifica se o token é válido e retorna dados do usuário autenticado."""
    from src.presentation.middlewares.auth_required import auth_required
    from flask import g

    @auth_required
    def _inner():
        return success({'user_id': g.user_id, 'username': g.username})

    return _inner()
