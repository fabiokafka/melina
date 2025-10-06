from flask import Blueprint, redirect, request, jsonify, session, url_for
from authlib.integrations.flask_client import OAuth
import os
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# Configurar OAuth
oauth = OAuth()

def init_oauth(app):
    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

# Lista de emails autorizados (será gerenciada via configurações)
AUTHORIZED_EMAILS = [
    'reservasmaremar@gmail.com.br',
]

AUTHORIZED_DOMAINS = [
    'pixelz.com.br',
]

def is_email_authorized(email):
    """Verifica se o email está autorizado"""
    if email.lower() in [e.lower() for e in AUTHORIZED_EMAILS]:
        return True
    
    email_domain = email.split('@')[1] if '@' in email else ''
    if email_domain.lower() in [d.lower() for d in AUTHORIZED_DOMAINS]:
        return True
    
    return False

def login_required(f):
    """Decorator para proteger rotas que precisam de autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'error': 'Não autenticado'}), 401
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login')
def login():
    """Inicia o fluxo de login OAuth com Google"""
    redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')
    # Forçar seleção de conta sempre
    return oauth.google.authorize_redirect(
        redirect_uri,
        prompt='select_account'
    )

@auth_bp.route('/callback')
def callback():
    """Callback do OAuth após autenticação"""
    try:
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo')
        
        if not user_info:
            return redirect('/?error=no_user_info')
        
        email = user_info.get('email')
        
        # Verificar se o email está autorizado
        if not is_email_authorized(email):
            return redirect('/?error=unauthorized')
        
        # Salvar informações do usuário na sessão
        session['user'] = {
            'email': email,
            'name': user_info.get('name'),
            'picture': user_info.get('picture'),
        }
        
        return redirect('/')
        
    except Exception as e:
        print(f"Erro no callback OAuth: {str(e)}")
        return redirect('/?error=auth_failed')

@auth_bp.route('/logout')
def logout():
    """Faz logout do usuário"""
    session.pop('user', None)
    return redirect('/')

@auth_bp.route('/user')
def get_user():
    """Retorna informações do usuário logado"""
    if 'user' in session:
        return jsonify(session['user'])
    return jsonify({'error': 'Não autenticado'}), 401

@auth_bp.route('/check')
def check_auth():
    """Verifica se o usuário está autenticado"""
    return jsonify({
        'authenticated': 'user' in session,
        'user': session.get('user')
    })
