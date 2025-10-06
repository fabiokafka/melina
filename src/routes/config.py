from flask import Blueprint, jsonify, request
import os
import requests
from src.routes.auth import login_required

config_bp = Blueprint('config', __name__)

@config_bp.route('/paytour/credentials', methods=['GET'])
@login_required
def get_paytour_credentials():
    """Retorna as credenciais da Paytour (mascaradas)"""
    api_key = os.getenv('PAYTOUR_API_KEY', '')
    api_secret = os.getenv('PAYTOUR_API_SECRET', '')
    
    # Mascarar credenciais
    masked_key = api_key[:10] + '...' + api_key[-10:] if len(api_key) > 20 else api_key
    masked_secret = api_secret[:10] + '...' + api_secret[-10:] if len(api_secret) > 20 else api_secret
    
    return jsonify({
        'api_key': masked_key,
        'api_secret': masked_secret,
        'api_url': os.getenv('PAYTOUR_API_URL', 'https://api.paytour.com.br/v2')
    })

@config_bp.route('/paytour/test-connection', methods=['POST'])
@login_required
def test_paytour_connection():
    """Testa a conexão com a API Paytour"""
    try:
        base64_auth = os.getenv('PAYTOUR_API_BASE64')
        api_url = os.getenv('PAYTOUR_API_URL', 'https://api.paytour.com.br/v2')
        
        # Tentar fazer login na API
        response = requests.post(
            f'{api_url}/lojas/login?grant_type=application',
            headers={
                'Authorization': f'Basic {base64_auth}',
                'Content-Type': 'application/json'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'status': 'success',
                'message': 'Conexão estabelecida com sucesso!',
                'loja': data.get('loja', {}).get('nome', 'N/A')
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Erro na autenticação: {response.status_code}',
                'details': response.text
            }), 400
            
    except requests.exceptions.Timeout:
        return jsonify({
            'status': 'error',
            'message': 'Timeout ao conectar com a API Paytour'
        }), 408
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao testar conexão: {str(e)}'
        }), 500

@config_bp.route('/authorized-emails', methods=['GET'])
@login_required
def get_authorized_emails():
    """Retorna lista de emails autorizados"""
    from src.routes.auth import AUTHORIZED_EMAILS, AUTHORIZED_DOMAINS
    
    return jsonify({
        'emails': AUTHORIZED_EMAILS,
        'domains': AUTHORIZED_DOMAINS
    })

@config_bp.route('/authorized-emails', methods=['POST'])
@login_required
def add_authorized_email():
    """Adiciona um email à lista de autorizados"""
    from src.routes.auth import AUTHORIZED_EMAILS
    
    data = request.json
    email = data.get('email', '').strip().lower()
    
    if not email or '@' not in email:
        return jsonify({'error': 'Email inválido'}), 400
    
    if email not in [e.lower() for e in AUTHORIZED_EMAILS]:
        AUTHORIZED_EMAILS.append(email)
        return jsonify({
            'message': 'Email adicionado com sucesso',
            'emails': AUTHORIZED_EMAILS
        })
    
    return jsonify({'message': 'Email já existe na lista'}), 200

@config_bp.route('/authorized-emails/<email>', methods=['DELETE'])
@login_required
def remove_authorized_email(email):
    """Remove um email da lista de autorizados"""
    from src.routes.auth import AUTHORIZED_EMAILS
    
    email = email.strip().lower()
    
    # Não permitir remover o email principal
    if email == 'reservasmaremar@gmail.com.br':
        return jsonify({'error': 'Não é possível remover o email principal'}), 403
    
    AUTHORIZED_EMAILS[:] = [e for e in AUTHORIZED_EMAILS if e.lower() != email]
    
    return jsonify({
        'message': 'Email removido com sucesso',
        'emails': AUTHORIZED_EMAILS
    })

@config_bp.route('/authorized-domains', methods=['POST'])
@login_required
def add_authorized_domain():
    """Adiciona um domínio à lista de autorizados"""
    from src.routes.auth import AUTHORIZED_DOMAINS
    
    data = request.json
    domain = data.get('domain', '').strip().lower()
    
    if not domain or '.' not in domain:
        return jsonify({'error': 'Domínio inválido'}), 400
    
    if domain not in [d.lower() for d in AUTHORIZED_DOMAINS]:
        AUTHORIZED_DOMAINS.append(domain)
        return jsonify({
            'message': 'Domínio adicionado com sucesso',
            'domains': AUTHORIZED_DOMAINS
        })
    
    return jsonify({'message': 'Domínio já existe na lista'}), 200

@config_bp.route('/authorized-domains/<domain>', methods=['DELETE'])
@login_required
def remove_authorized_domain(domain):
    """Remove um domínio da lista de autorizados"""
    from src.routes.auth import AUTHORIZED_DOMAINS
    
    domain = domain.strip().lower()
    
    # Não permitir remover o domínio principal
    if domain == 'pixelz.com.br':
        return jsonify({'error': 'Não é possível remover o domínio principal'}), 403
    
    AUTHORIZED_DOMAINS[:] = [d for d in AUTHORIZED_DOMAINS if d.lower() != domain]
    
    return jsonify({
        'message': 'Domínio removido com sucesso',
        'domains': AUTHORIZED_DOMAINS
    })
