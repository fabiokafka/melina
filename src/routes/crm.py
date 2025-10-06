"""
Rotas para CRM - INTEGRAÇÃO REAL
Clientes da Paytour + Cadastro local + Campanhas com IA
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
import sys
import os
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.paytour_service import PaytourService
from services.ai_service import AIService

crm_bp = Blueprint('crm', __name__, url_prefix='/api/crm')

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'app.db')

def init_db():
    """Inicializa tabela de clientes se não existir"""
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                telefone TEXT,
                cpf TEXT,
                data_nascimento TEXT,
                cidade TEXT,
                estado TEXT,
                origem TEXT DEFAULT 'cadastro_manual',
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultima_compra TIMESTAMP,
                total_compras INTEGER DEFAULT 0,
                valor_total REAL DEFAULT 0,
                status TEXT DEFAULT 'ativo',
                observacoes TEXT
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao inicializar DB: {str(e)}")

# Inicializar DB
init_db()

@crm_bp.route('/clientes', methods=['GET'])
def listar_clientes():
    """Lista todos os clientes (Paytour + Cadastro local)"""
    try:
        # Buscar clientes do banco local
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Parâmetros de filtro
        status = request.args.get('status', 'ativo')
        busca = request.args.get('busca', '')
        
        query = 'SELECT * FROM clientes WHERE status = ?'
        params = [status]
        
        if busca:
            query += ' AND (nome LIKE ? OR email LIKE ? OR telefone LIKE ?)'
            params.extend([f'%{busca}%', f'%{busca}%', f'%{busca}%'])
        
        query += ' ORDER BY data_cadastro DESC LIMIT 100'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        clientes = []
        for row in rows:
            clientes.append({
                'id': row['id'],
                'nome': row['nome'],
                'email': row['email'],
                'telefone': row['telefone'],
                'cpf': row['cpf'],
                'data_nascimento': row['data_nascimento'],
                'cidade': row['cidade'],
                'estado': row['estado'],
                'origem': row['origem'],
                'data_cadastro': row['data_cadastro'],
                'ultima_compra': row['ultima_compra'],
                'total_compras': row['total_compras'],
                'valor_total': row['valor_total'],
                'status': row['status']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'clientes': clientes,
            'total': len(clientes)
        }), 200
        
    except Exception as e:
        print(f"Erro ao listar clientes: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@crm_bp.route('/clientes', methods=['POST'])
def cadastrar_cliente():
    """Cadastra novo cliente"""
    try:
        data = request.get_json()
        
        # Validar campos obrigatórios
        if not data.get('nome') or not data.get('email'):
            return jsonify({
                'success': False,
                'error': 'Nome e email são obrigatórios'
            }), 400
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se email já existe
        cursor.execute('SELECT id FROM clientes WHERE email = ?', (data.get('email'),))
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Email já cadastrado'
            }), 400
        
        # Inserir cliente
        cursor.execute('''
            INSERT INTO clientes (
                nome, email, telefone, cpf, data_nascimento,
                cidade, estado, origem, observacoes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('nome'),
            data.get('email'),
            data.get('telefone', ''),
            data.get('cpf', ''),
            data.get('data_nascimento', ''),
            data.get('cidade', ''),
            data.get('estado', ''),
            data.get('origem', 'cadastro_manual'),
            data.get('observacoes', '')
        ))
        
        cliente_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Cliente cadastrado com sucesso',
            'cliente_id': cliente_id
        }), 201
        
    except Exception as e:
        print(f"Erro ao cadastrar cliente: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@crm_bp.route('/campanhas/criar', methods=['POST'])
def criar_campanha():
    """Cria campanha de marketing com IA"""
    try:
        data = request.get_json()
        
        tipo = data.get('tipo', 'email')
        publico = data.get('publico', 'todos')
        objetivo = data.get('objetivo', 'engajamento')
        
        ai_service = AIService()
        
        # Buscar informações dos clientes
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        if publico == 'inativos':
            cursor.execute('''
                SELECT COUNT(*) FROM clientes 
                WHERE ultima_compra IS NULL 
                OR datetime(ultima_compra) < datetime('now', '-60 days')
            ''')
        elif publico == 'vips':
            cursor.execute('SELECT COUNT(*) FROM clientes WHERE total_compras >= 5')
        else:
            cursor.execute('SELECT COUNT(*) FROM clientes WHERE status = "ativo"')
        
        result = cursor.fetchone()
        total_destinatarios = result[0] if result else 0
        conn.close()
        
        # Gerar campanha com IA
        prompt = f"""
        Crie uma campanha de {tipo} para a Maremar Turismo com os seguintes parâmetros:
        
        - Público-alvo: {publico} ({total_destinatarios} pessoas)
        - Objetivo: {objetivo}
        - Tipo: {tipo}
        
        A Maremar Turismo oferece passeios de barco em Ilhabela.
        
        Forneça:
        1. Assunto/Título
        2. Corpo da mensagem (máximo 200 palavras)
        3. Call-to-action claro
        
        Tom: Amigável, entusiasmado, focado em experiências.
        """
        
        campanha = ai_service.generate_text(prompt)
        
        return jsonify({
            'success': True,
            'campanha': {
                'tipo': tipo,
                'publico': publico,
                'objetivo': objetivo,
                'total_destinatarios': total_destinatarios,
                'conteudo': campanha,
                'data_criacao': datetime.now().isoformat()
            }
        }), 200
        
    except Exception as e:
        print(f"Erro ao criar campanha: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@crm_bp.route('/estatisticas', methods=['GET'])
def estatisticas_crm():
    """Estatísticas gerais do CRM"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Total de clientes
        cursor.execute('SELECT COUNT(*) FROM clientes WHERE status = "ativo"')
        result = cursor.fetchone()
        total_clientes = result[0] if result else 0
        
        # Clientes novos (últimos 30 dias)
        cursor.execute('''
            SELECT COUNT(*) FROM clientes 
            WHERE status = "ativo" 
            AND datetime(data_cadastro) >= datetime('now', '-30 days')
        ''')
        result = cursor.fetchone()
        clientes_novos = result[0] if result else 0
        
        conn.close()
        
        return jsonify({
            'success': True,
            'estatisticas': {
                'total_clientes': total_clientes,
                'clientes_novos_mes': clientes_novos
            }
        }), 200
        
    except Exception as e:
        print(f"Erro ao buscar estatísticas: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
