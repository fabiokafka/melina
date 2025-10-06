"""
Rotas para painel financeiro - INTEGRAÇÃO REAL PAYTOUR
Cálculo baseado em disponibilidade (vagas vendidas = total - disponível)
"""
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.paytour_service import PaytourService
from services.ai_service import AIService

financeiro_bp = Blueprint('financeiro', __name__, url_prefix='/api/financeiro')

@financeiro_bp.route('/vendas', methods=['GET'])
def listar_vendas():
    """Lista vendas estimadas por passeio baseado em disponibilidade"""
    try:
        paytour = PaytourService()
        
        # Parâmetros
        periodo = request.args.get('periodo', 'mes')  # dia, semana, mes
        
        # Buscar todos os passeios
        hoje = datetime.now().strftime('%Y-%m-%d')
        um_mes = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        result = paytour.get_passeios(data_de=hoje, data_ate=um_mes)
        passeios_list = result.get('passeios', [])
        
        # Calcular vendas para cada passeio
        vendas = []
        total_vendas = 0
        total_receita = 0
        
        for passeio in passeios_list[:15]:  # Limitar para performance
            passeio_id = passeio.get('id')
            titulo = passeio.get('titulo', 'Sem título')
            
            # Calcular vendas estimadas
            venda_info = paytour.calcular_vendas_estimadas(passeio_id, periodo=periodo)
            
            if venda_info['vagas_vendidas'] > 0:
                vendas.append({
                    'passeio_id': passeio_id,
                    'titulo': titulo,
                    'vagas_vendidas': venda_info['vagas_vendidas'],
                    'preco_medio': venda_info['preco_medio'],
                    'receita': venda_info['receita_estimada'],
                    'periodo': periodo
                })
                
                total_vendas += venda_info['vagas_vendidas']
                total_receita += venda_info['receita_estimada']
        
        return jsonify({
            'success': True,
            'vendas': vendas,
            'resumo': {
                'total_vendas': total_vendas,
                'total_receita': round(total_receita, 2),
                'periodo': periodo
            }
        }), 200
        
    except Exception as e:
        print(f"Erro ao listar vendas: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@financeiro_bp.route('/resumo', methods=['GET'])
def resumo_financeiro():
    """Resumo financeiro com KPIs principais"""
    try:
        paytour = PaytourService()
        
        # Buscar passeios
        hoje = datetime.now().strftime('%Y-%m-%d')
        um_mes = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        result = paytour.get_passeios(data_de=hoje, data_ate=um_mes)
        passeios_list = result.get('passeios', [])
        
        # Calcular métricas
        total_passeios = len(passeios_list)
        total_vendas_mes = 0
        total_receita_mes = 0
        total_vendas_semana = 0
        total_receita_semana = 0
        
        passeios_mais_vendidos = []
        
        for passeio in passeios_list[:15]:
            passeio_id = passeio.get('id')
            titulo = passeio.get('titulo', '')
            
            # Vendas do mês
            vendas_mes = paytour.calcular_vendas_estimadas(passeio_id, periodo='mes')
            total_vendas_mes += vendas_mes['vagas_vendidas']
            total_receita_mes += vendas_mes['receita_estimada']
            
            # Vendas da semana
            vendas_semana = paytour.calcular_vendas_estimadas(passeio_id, periodo='semana')
            total_vendas_semana += vendas_semana['vagas_vendidas']
            total_receita_semana += vendas_semana['receita_estimada']
            
            if vendas_mes['vagas_vendidas'] > 0:
                passeios_mais_vendidos.append({
                    'titulo': titulo,
                    'vendas': vendas_mes['vagas_vendidas'],
                    'receita': vendas_mes['receita_estimada']
                })
        
        # Ordenar por vendas
        passeios_mais_vendidos.sort(key=lambda x: x['vendas'], reverse=True)
        
        # Calcular crescimento (mock - precisaria de dados históricos)
        crescimento_vendas = 15.5  # Placeholder
        crescimento_receita = 18.2  # Placeholder
        
        return jsonify({
            'success': True,
            'resumo': {
                'total_passeios': total_passeios,
                'vendas_mes': total_vendas_mes,
                'receita_mes': round(total_receita_mes, 2),
                'vendas_semana': total_vendas_semana,
                'receita_semana': round(total_receita_semana, 2),
                'ticket_medio': round(total_receita_mes / total_vendas_mes, 2) if total_vendas_mes > 0 else 0,
                'crescimento_vendas': crescimento_vendas,
                'crescimento_receita': crescimento_receita,
                'passeios_mais_vendidos': passeios_mais_vendidos[:5]
            }
        }), 200
        
    except Exception as e:
        print(f"Erro ao gerar resumo financeiro: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@financeiro_bp.route('/analise', methods=['POST'])
def analise_ia():
    """Análise financeira com IA"""
    try:
        data = request.get_json()
        periodo = data.get('periodo', 'mes')
        
        paytour = PaytourService()
        ai_service = AIService()
        
        # Buscar dados financeiros
        hoje = datetime.now().strftime('%Y-%m-%d')
        um_mes = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        result = paytour.get_passeios(data_de=hoje, data_ate=um_mes)
        passeios_list = result.get('passeios', [])
        
        # Coletar dados para análise
        dados_analise = []
        total_receita = 0
        
        for passeio in passeios_list[:10]:
            passeio_id = passeio.get('id')
            titulo = passeio.get('titulo', '')
            
            vendas = paytour.calcular_vendas_estimadas(passeio_id, periodo=periodo)
            
            if vendas['vagas_vendidas'] > 0:
                dados_analise.append({
                    'passeio': titulo,
                    'vendas': vendas['vagas_vendidas'],
                    'receita': vendas['receita_estimada']
                })
                total_receita += vendas['receita_estimada']
        
        # Gerar análise com IA
        prompt = f"""
        Analise os seguintes dados financeiros da Maremar Turismo para o período de {periodo}:
        
        Dados de vendas:
        {dados_analise}
        
        Receita total: R$ {total_receita:.2f}
        
        Forneça:
        1. Análise geral do desempenho
        2. Principais insights
        3. Recomendações estratégicas
        4. Oportunidades de crescimento
        
        Seja objetivo e focado em ações práticas.
        """
        
        analise = ai_service.analyze_data(dados_analise, prompt)
        
        return jsonify({
            'success': True,
            'analise': analise,
            'dados': {
                'periodo': periodo,
                'total_receita': round(total_receita, 2),
                'passeios_analisados': len(dados_analise)
            }
        }), 200
        
    except Exception as e:
        print(f"Erro na análise com IA: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@financeiro_bp.route('/relatorio', methods=['POST'])
def gerar_relatorio():
    """Gera relatório financeiro detalhado"""
    try:
        data = request.get_json()
        data_inicio = data.get('data_inicio')
        data_fim = data.get('data_fim')
        formato = data.get('formato', 'json')  # json, pdf, excel
        
        paytour = PaytourService()
        
        # Se não informado, usar último mês
        if not data_inicio:
            data_inicio = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not data_fim:
            data_fim = datetime.now().strftime('%Y-%m-%d')
        
        # Buscar dados
        result = paytour.get_passeios(data_de=data_inicio, data_ate=data_fim)
        passeios_list = result.get('passeios', [])
        
        # Gerar relatório
        relatorio = {
            'periodo': {
                'inicio': data_inicio,
                'fim': data_fim
            },
            'resumo': {
                'total_passeios': len(passeios_list),
                'total_vendas': 0,
                'total_receita': 0
            },
            'detalhes': []
        }
        
        for passeio in passeios_list[:20]:
            passeio_id = passeio.get('id')
            titulo = passeio.get('titulo', '')
            
            vendas = paytour.calcular_vendas_estimadas(passeio_id, periodo='mes')
            
            relatorio['resumo']['total_vendas'] += vendas['vagas_vendidas']
            relatorio['resumo']['total_receita'] += vendas['receita_estimada']
            
            relatorio['detalhes'].append({
                'passeio': titulo,
                'vendas': vendas['vagas_vendidas'],
                'preco_medio': vendas['preco_medio'],
                'receita': vendas['receita_estimada']
            })
        
        relatorio['resumo']['total_receita'] = round(relatorio['resumo']['total_receita'], 2)
        
        # TODO: Implementar geração de PDF/Excel se necessário
        
        return jsonify({
            'success': True,
            'relatorio': relatorio,
            'formato': formato
        }), 200
        
    except Exception as e:
        print(f"Erro ao gerar relatório: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@financeiro_bp.route('/grafico-vendas', methods=['GET'])
def grafico_vendas():
    """Dados para gráfico de vendas ao longo do tempo"""
    try:
        paytour = PaytourService()
        
        # Últimos 30 dias
        dados_grafico = []
        
        for i in range(30, 0, -1):
            data = datetime.now() - timedelta(days=i)
            data_str = data.strftime('%Y-%m-%d')
            
            # Buscar passeios para este dia
            result = paytour.get_passeios(data_de=data_str, data_ate=data_str)
            passeios_list = result.get('passeios', [])
            
            vendas_dia = 0
            receita_dia = 0
            
            for passeio in passeios_list[:5]:  # Limitar para performance
                passeio_id = passeio.get('id')
                vendas = paytour.calcular_vendas_estimadas(passeio_id, periodo='dia')
                vendas_dia += vendas['vagas_vendidas']
                receita_dia += vendas['receita_estimada']
            
            dados_grafico.append({
                'data': data_str,
                'vendas': vendas_dia,
                'receita': round(receita_dia, 2)
            })
        
        return jsonify({
            'success': True,
            'dados': dados_grafico
        }), 200
        
    except Exception as e:
        print(f"Erro ao gerar dados do gráfico: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
