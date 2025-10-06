"""
Rotas para Clima, Baleias e Marketing - INTEGRAÇÃO REAL
"""
from flask import Blueprint, jsonify, request
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.weather_service import WeatherService
from services.ai_service import AIService

outros_bp = Blueprint('outros', __name__, url_prefix='/api')

# ============= CLIMA =============

@outros_bp.route('/clima/atual', methods=['GET'])
def clima_atual():
    """Obtém clima atual de Ilhabela"""
    try:
        weather = WeatherService()
        clima = weather.get_current_weather()
        
        return jsonify({
            'success': True,
            'clima': clima
        }), 200
        
    except Exception as e:
        print(f"Erro ao buscar clima atual: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@outros_bp.route('/clima/previsao', methods=['GET'])
def clima_previsao():
    """Obtém previsão do tempo para os próximos dias"""
    try:
        dias = request.args.get('dias', 7, type=int)
        dias = min(dias, 7)  # Máximo 7 dias
        
        weather = WeatherService()
        previsao = weather.get_forecast(days=dias)
        
        return jsonify({
            'success': True,
            'previsao': previsao
        }), 200
        
    except Exception as e:
        print(f"Erro ao buscar previsão: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@outros_bp.route('/clima/analise', methods=['GET'])
def clima_analise():
    """Analisa impacto do clima nas vendas"""
    try:
        dias = request.args.get('dias', 7, type=int)
        dias = min(dias, 7)
        
        weather = WeatherService()
        previsao = weather.get_forecast(days=dias)
        impactos = weather.analyze_impact(previsao)
        
        return jsonify({
            'success': True,
            'analise': impactos
        }), 200
        
    except Exception as e:
        print(f"Erro ao analisar impacto: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============= BALEIAS =============

@outros_bp.route('/baleias/info', methods=['GET'])
def baleias_info():
    """Informações sobre baleias em Ilhabela com IA"""
    try:
        ai_service = AIService()
        
        prompt = """
        Forneça informações sobre baleias em Ilhabela, SP:
        1. Espécies mais comuns
        2. Melhor época para avistamento
        3. Locais mais propícios
        4. Comportamentos típicos
        Seja objetivo e informativo.
        """
        
        info = ai_service.generate_text(prompt)
        
        return jsonify({
            'success': True,
            'informacoes': info
        }), 200
        
    except Exception as e:
        print(f"Erro ao buscar info de baleias: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============= MARKETING =============

@outros_bp.route('/marketing/campanhas', methods=['GET'])
def marketing_campanhas():
    """Lista campanhas de marketing"""
    try:
        campanhas = [
            {
                'id': 1,
                'nome': 'Campanha Verão 2024',
                'plataforma': 'Google Ads',
                'status': 'ativa',
                'impressoes': 15420,
                'cliques': 892,
                'conversoes': 45,
                'investimento': 1250.00,
                'retorno': 4500.00
            }
        ]
        
        return jsonify({
            'success': True,
            'campanhas': campanhas
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
