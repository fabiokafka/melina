"""
Rotas para gerenciamento de passeios - INTEGRAÇÃO REAL PAYTOUR
"""
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import sys
import os

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.paytour_service import PaytourService

passeios_bp = Blueprint('passeios', __name__, url_prefix='/api/passeios')

@passeios_bp.route('/', methods=['GET'])
def listar_passeios():
    """Lista todos os passeios disponíveis da API Paytour"""
    try:
        paytour = PaytourService()
        
        # Parâmetros opcionais
        data_de = request.args.get('data_de')
        data_ate = request.args.get('data_ate')
        
        # Se não informado, buscar próximos 3 meses
        if not data_de:
            data_de = datetime.now().strftime('%Y-%m-%d')
        if not data_ate:
            data_ate = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
        
        # Buscar passeios na API Paytour
        result = paytour.get_passeios(data_de=data_de, data_ate=data_ate)
        
        passeios_list = result.get('passeios', [])
        
        return jsonify({
            'success': True,
            'passeios': passeios_list,
            'total': len(passeios_list)
        }), 200
        
    except Exception as e:
        print(f"Erro ao listar passeios: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'passeios': []
        }), 500

@passeios_bp.route('/<int:passeio_id>', methods=['GET'])
def detalhar_passeio(passeio_id):
    """Obtém detalhes completos de um passeio da API Paytour"""
    try:
        paytour = PaytourService()
        
        meses = request.args.get('meses', 3, type=int)
        
        # Buscar detalhes na API Paytour
        passeio = paytour.get_passeio_detalhes(passeio_id, meses=meses)
        
        if not passeio:
            return jsonify({
                'success': False,
                'error': 'Passeio não encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'passeio': passeio
        }), 200
        
    except Exception as e:
        print(f"Erro ao detalhar passeio: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@passeios_bp.route('/<int:passeio_id>/disponibilidade', methods=['GET'])
def disponibilidade_passeio(passeio_id):
    """Obtém disponibilidade de vagas de um passeio"""
    try:
        paytour = PaytourService()
        
        # Calcular disponibilidade (dia, semana, mês)
        disponibilidade = paytour.get_disponibilidade_resumo(passeio_id)
        
        return jsonify({
            'success': True,
            'passeio_id': passeio_id,
            'disponibilidade': disponibilidade
        }), 200
        
    except Exception as e:
        print(f"Erro ao buscar disponibilidade: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@passeios_bp.route('/resumo', methods=['GET'])
def resumo_passeios():
    """Retorna resumo de todos os passeios com disponibilidade (dia/semana/mês)"""
    try:
        paytour = PaytourService()
        
        # Buscar todos os passeios
        hoje = datetime.now().strftime('%Y-%m-%d')
        um_mes = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        result = paytour.get_passeios(data_de=hoje, data_ate=um_mes)
        passeios_list = result.get('passeios', [])
        
        # Processar resumo com disponibilidade
        resumo = []
        
        for passeio in passeios_list:  # Processar todos os passeios
            passeio_id = passeio.get('id')
            
            # Buscar disponibilidade
            disp = paytour.get_disponibilidade_resumo(passeio_id)
            
            resumo.append({
                'id': passeio_id,
                'titulo': passeio.get('nome', passeio.get('titulo', 'Sem título')),
                'preco': float(passeio.get('preco_exibicao', 0)),
                'icone': passeio.get('icone', 'ship'),
                'foto': passeio.get('foto_capa', ''),
                'url': passeio.get('url', ''),
                'vagas_dia': disp.get('vagas_dia', 0),
                'vagas_semana': disp.get('vagas_semana', 0),
                'vagas_mes': disp.get('vagas_mes', 0)
            })
        
        return jsonify({
            'success': True,
            'passeios': resumo
        }), 200
        
    except Exception as e:
        print(f"Erro ao gerar resumo: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'passeios': []
        }), 500

@passeios_bp.route('/<int:passeio_id>/vendas', methods=['GET'])
def vendas_passeio(passeio_id):
    """Calcula vendas estimadas de um passeio baseado em disponibilidade"""
    try:
        paytour = PaytourService()
        
        periodo = request.args.get('periodo', 'mes')  # dia, semana, mes
        
        # Calcular vendas estimadas
        vendas = paytour.calcular_vendas_estimadas(passeio_id, periodo=periodo)
        
        return jsonify({
            'success': True,
            'passeio_id': passeio_id,
            'periodo': periodo,
            'vendas': vendas
        }), 200
        
    except Exception as e:
        print(f"Erro ao calcular vendas: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
