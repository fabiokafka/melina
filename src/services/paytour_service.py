import os
import requests
from datetime import datetime, timedelta
import base64

class PaytourService:
    def __init__(self):
        self.base_url = os.getenv('PAYTOUR_API_URL', 'https://api.paytour.com.br/v2')
        self.api_key = os.getenv('PAYTOUR_API_KEY')
        self.api_secret = os.getenv('PAYTOUR_API_SECRET')
        self.access_token = None
        self.token_expires_at = None
    
    def _get_auth_header(self):
        """Gera header de autenticação Basic"""
        credentials = f"{self.api_key}:{self.api_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"
    
    def authenticate(self):
        """Autentica na API Paytour e obtém Bearer token"""
        try:
            # Verificar se já tem token válido
            if self.access_token and self.token_expires_at:
                if datetime.now() < self.token_expires_at:
                    return True
            
            url = f"{self.base_url}/lojas/login"
            headers = {
                'Authorization': self._get_auth_header(),
                'Content-Type': 'application/json'
            }
            params = {'grant_type': 'application'}
            
            response = requests.post(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                # Token expira em 30 minutos (1800 segundos)
                expires_in = data.get('expires_in', 1800)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                return True
            else:
                print(f"Erro na autenticação Paytour: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Exceção na autenticação Paytour: {str(e)}")
            return False
    
    def _get_headers(self):
        """Retorna headers com Bearer token"""
        if not self.authenticate():
            raise Exception("Falha na autenticação Paytour")
        
        return {
            'Authorization': f"Bearer {self.access_token}",
            'Content-Type': 'application/json'
        }
    
    def get_passeios(self, data_de=None, data_ate=None, pagina=1, quantidade=50):
        """
        Lista todos os passeios da Maremar
        
        Resposta vem em formato:
        {
            "itens": [...],
            "info": {"total": X, "pagina": Y, "total_paginas": Z}
        }
        """
        try:
            url = f"{self.base_url}/passeios"
            headers = self._get_headers()
            
            params = {
                'pagina': pagina,
                'quantidade': quantidade,
                'minimalResponse': 0
            }
            
            if data_de:
                params['data_de'] = data_de
            if data_ate:
                params['data_ate'] = data_ate
            
            response = requests.get(url, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                # Retornar no formato esperado
                return {
                    'passeios': data.get('itens', []),
                    'info': data.get('info', {})
                }
            else:
                print(f"Erro ao buscar passeios: {response.status_code} - {response.text}")
                return {'passeios': [], 'info': {}}
                
        except Exception as e:
            print(f"Exceção ao buscar passeios: {str(e)}")
            return {'passeios': [], 'info': {}}
    
    def get_passeio_detalhes(self, passeio_id, meses=3):
        """
        Obtém detalhes de um passeio específico incluindo disponibilidade
        """
        try:
            url = f"{self.base_url}/passeios/{passeio_id}"
            headers = self._get_headers()
            params = {'disponibilidadeAte': min(meses, 12)}
            
            response = requests.get(url, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Erro ao buscar detalhes do passeio {passeio_id}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Exceção ao buscar detalhes do passeio: {str(e)}")
            return None
    
    def get_disponibilidade_resumo(self, passeio_id):
        """
        Calcula resumo de disponibilidade (dia, semana, mês)
        """
        try:
            detalhes = self.get_passeio_detalhes(passeio_id, meses=1)
            
            if not detalhes or 'disponibilidades' not in detalhes:
                return {'vagas_dia': 0, 'vagas_semana': 0, 'vagas_mes': 0}
            
            hoje = datetime.now().date()
            uma_semana = hoje + timedelta(days=7)
            um_mes = hoje + timedelta(days=30)
            
            vagas_dia = 0
            vagas_semana = 0
            vagas_mes = 0
            
            for disp in detalhes.get('disponibilidades', []):
                data_str = disp.get('data')
                if not data_str:
                    continue
                
                try:
                    data = datetime.strptime(data_str, '%Y-%m-%d').date()
                    vagas = int(disp.get('vagas_disponiveis', 0))
                    
                    # Vagas do dia
                    if data == hoje:
                        vagas_dia += vagas
                    
                    # Vagas da semana
                    if hoje <= data <= uma_semana:
                        vagas_semana += vagas
                    
                    # Vagas do mês
                    if hoje <= data <= um_mes:
                        vagas_mes += vagas
                        
                except ValueError:
                    continue
            
            return {
                'vagas_dia': vagas_dia,
                'vagas_semana': vagas_semana,
                'vagas_mes': vagas_mes
            }
            
        except Exception as e:
            print(f"Exceção ao calcular disponibilidade: {str(e)}")
            return {'vagas_dia': 0, 'vagas_semana': 0, 'vagas_mes': 0}
    
    def calcular_vendas_estimadas(self, passeio_id, periodo='mes'):
        """
        Calcula vendas estimadas baseado em disponibilidade
        
        Estratégia: Assumir capacidade total e subtrair vagas disponíveis
        """
        try:
            detalhes = self.get_passeio_detalhes(passeio_id, meses=1)
            
            if not detalhes:
                return {'vagas_vendidas': 0, 'receita_estimada': 0, 'preco_medio': 0}
            
            # Obter preço médio
            preco_medio = float(detalhes.get('preco_exibicao', 0))
            
            # Calcular capacidade total e vagas disponíveis
            hoje = datetime.now().date()
            
            if periodo == 'dia':
                data_limite = hoje
            elif periodo == 'semana':
                data_limite = hoje + timedelta(days=7)
            else:  # mes
                data_limite = hoje + timedelta(days=30)
            
            capacidade_total = 0
            vagas_disponiveis = 0
            
            for disp in detalhes.get('disponibilidades', []):
                data_str = disp.get('data')
                if not data_str:
                    continue
                
                try:
                    data = datetime.strptime(data_str, '%Y-%m-%d').date()
                    
                    if hoje <= data <= data_limite:
                        # Capacidade total (assumir 10 vagas por dia se não informado)
                        capacidade = int(disp.get('vagas_totais', 10))
                        vagas_disp = int(disp.get('vagas_disponiveis', 0))
                        
                        capacidade_total += capacidade
                        vagas_disponiveis += vagas_disp
                        
                except ValueError:
                    continue
            
            # Vagas vendidas = capacidade total - vagas disponíveis
            vagas_vendidas = max(0, capacidade_total - vagas_disponiveis)
            receita_estimada = vagas_vendidas * preco_medio
            
            return {
                'vagas_vendidas': vagas_vendidas,
                'receita_estimada': round(receita_estimada, 2),
                'preco_medio': round(preco_medio, 2)
            }
            
        except Exception as e:
            print(f"Exceção ao calcular vendas: {str(e)}")
            return {'vagas_vendidas': 0, 'receita_estimada': 0, 'preco_medio': 0}
    
    def test_connection(self):
        """Testa conexão com a API Paytour"""
        try:
            if self.authenticate():
                # Tentar buscar passeios
                result = self.get_passeios(quantidade=1)
                
                if result.get('passeios'):
                    return {
                        'status': 'success',
                        'message': 'Conexão estabelecida com sucesso!',
                        'total_passeios': result.get('info', {}).get('total', 0)
                    }
                else:
                    return {
                        'status': 'warning',
                        'message': 'Conectado mas nenhum passeio encontrado'
                    }
            else:
                return {
                    'status': 'error',
                    'message': 'Falha na autenticação'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Erro: {str(e)}'
            }
