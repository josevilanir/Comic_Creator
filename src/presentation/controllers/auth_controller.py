"""
Auth Controller - Controller para autenticação
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from src.domain.entities import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Username e senha são obrigatórios.', 'error')
            return render_template('login.html')
        
        # Busca usuário
        container = current_app.container
        user = container.user_repository.buscar_por_username(username)
        
        if user and container.hash_service.verificar_password(password, user.password_hash):
            # Login bem-sucedido
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('download.index'))
        else:
            flash('Credenciais inválidas.', 'error')
    
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """Logout"""
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('download.index'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registro de novo usuário"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        password_confirm = request.form.get('password_confirm', '').strip()
        
        if not username or not password:
            flash('Username e senha são obrigatórios.', 'error')
            return render_template('register.html')
        
        if password != password_confirm:
            flash('Senhas não conferem.', 'error')
            return render_template('register.html')
        
        container = current_app.container
        
        # Valida força da senha
        valido, msg = container.hash_service.validar_forca_senha(password)
        if not valido:
            flash(msg, 'error')
            return render_template('register.html')
        
        try:
            # Cria usuário
            password_hash = container.hash_service.hash_password(password)
            user = User(
                id=None,
                username=username,
                password_hash=password_hash
            )
            container.user_repository.criar(user)
            
            flash('Usuário criado com sucesso! Faça login.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            flash(f'Erro ao criar usuário: {str(e)}', 'error')
    
    return render_template('register.html')