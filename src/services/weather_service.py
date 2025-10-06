import os
import requests
from datetime import datetime, timedelta

class WeatherService:
    """
    Serviço de previsão do tempo usando OpenWeather API
    API gratuita: https://openweathermap.org/api
    """
    
    def __init__(self):
        # API Key gratuita (1000 chamadas/dia)
        # Você pode criar sua própria em: https://openweathermap.org/api
        self.api_key = os.getenv('OPENWEATHER_API_KEY', 'demo')  # Usar 'demo' para testes
        self.base_url = 'https://api.openweathermap.org/data/2.5'
        
        # Coordenadas de Ilhabela, SP
        self.lat = -23.7781
        self.lon = -45.3581
    
    def get_current_weather(self):
        """Obtém clima atual de Ilhabela"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                'lat': self.lat,
                'lon': self.lon,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'pt_br'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'temperatura': round(data['main']['temp'], 1),
                    'sensacao': round(data['main']['feels_like'], 1),
                    'umidade': data['main']['humidity'],
                    'descricao': data['weather'][0]['description'].capitalize(),
                    'icone': data['weather'][0]['icon'],
                    'vento': round(data['wind']['speed'] * 3.6, 1),  # m/s para km/h
                    'visibilidade': data.get('visibility', 10000) / 1000,  # metros para km
                    'pressao': data['main']['pressure'],
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return self._get_mock_current_weather()
                
        except Exception as e:
            print(f"Erro ao buscar clima atual: {str(e)}")
            return self._get_mock_current_weather()
    
    def get_forecast(self, days=7):
        """Obtém previsão para os próximos dias"""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'lat': self.lat,
                'lon': self.lon,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'pt_br',
                'cnt': days * 8  # 8 previsões por dia (3h cada)
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                previsoes = []
                
                # Agrupar por dia
                dias = {}
                for item in data['list']:
                    dt = datetime.fromtimestamp(item['dt'])
                    dia = dt.date().isoformat()
                    
                    if dia not in dias:
                        dias[dia] = {
                            'data': dia,
                            'temp_min': item['main']['temp_min'],
                            'temp_max': item['main']['temp_max'],
                            'descricao': item['weather'][0]['description'].capitalize(),
                            'icone': item['weather'][0]['icon'],
                            'umidade': item['main']['humidity'],
                            'chuva_prob': item.get('pop', 0) * 100,  # Probabilidade de chuva
                            'vento': round(item['wind']['speed'] * 3.6, 1)
                        }
                    else:
                        # Atualizar min/max
                        dias[dia]['temp_min'] = min(dias[dia]['temp_min'], item['main']['temp_min'])
                        dias[dia]['temp_max'] = max(dias[dia]['temp_max'], item['main']['temp_max'])
                
                # Converter para lista
                for dia_data in sorted(dias.keys())[:days]:
                    dia_info = dias[dia_data]
                    previsoes.append({
                        'data': dia_info['data'],
                        'temp_min': round(dia_info['temp_min'], 1),
                        'temp_max': round(dia_info['temp_max'], 1),
                        'descricao': dia_info['descricao'],
                        'icone': dia_info['icone'],
                        'umidade': dia_info['umidade'],
                        'chuva_prob': round(dia_info['chuva_prob'], 0),
                        'vento': dia_info['vento']
                    })
                
                return previsoes
            else:
                return self._get_mock_forecast(days)
                
        except Exception as e:
            print(f"Erro ao buscar previsão: {str(e)}")
            return self._get_mock_forecast(days)
    
    def analyze_impact(self, forecast_data):
        """
        Analisa impacto do clima nas vendas de passeios
        
        Regras:
        - Chuva > 70%: Impacto negativo alto
        - Chuva 40-70%: Impacto negativo médio
        - Chuva < 40%: Impacto baixo
        - Temperatura ideal: 24-30°C
        - Vento > 30 km/h: Impacto negativo para passeios de barco
        """
        impactos = []
        
        for dia in forecast_data:
            score = 100  # Score inicial
            fatores = []
            
            # Análise de chuva
            chuva_prob = dia.get('chuva_prob', 0)
            if chuva_prob > 70:
                score -= 40
                fatores.append(f"Alta probabilidade de chuva ({chuva_prob:.0f}%)")
            elif chuva_prob > 40:
                score -= 20
                fatores.append(f"Probabilidade moderada de chuva ({chuva_prob:.0f}%)")
            
            # Análise de temperatura
            temp_max = dia.get('temp_max', 25)
            if temp_max < 20:
                score -= 15
                fatores.append(f"Temperatura baixa ({temp_max}°C)")
            elif temp_max > 35:
                score -= 10
                fatores.append(f"Temperatura muito alta ({temp_max}°C)")
            
            # Análise de vento
            vento = dia.get('vento', 0)
            if vento > 30:
                score -= 25
                fatores.append(f"Vento forte ({vento} km/h)")
            elif vento > 20:
                score -= 10
                fatores.append(f"Vento moderado ({vento} km/h)")
            
            # Classificação
            if score >= 80:
                classificacao = 'Excelente'
                cor = 'green'
            elif score >= 60:
                classificacao = 'Bom'
                cor = 'blue'
            elif score >= 40:
                classificacao = 'Regular'
                cor = 'yellow'
            else:
                classificacao = 'Ruim'
                cor = 'red'
            
            impactos.append({
                'data': dia['data'],
                'score': score,
                'classificacao': classificacao,
                'cor': cor,
                'fatores': fatores if fatores else ['Condições ideais para passeios'],
                'recomendacao': self._get_recommendation(score, dia)
            })
        
        return impactos
    
    def _get_recommendation(self, score, dia):
        """Gera recomendação baseada no score"""
        if score >= 80:
            return "Dia ideal para todos os tipos de passeios. Promova passeios de barco e praia."
        elif score >= 60:
            return "Boas condições. Foque em passeios ao ar livre."
        elif score >= 40:
            return "Condições regulares. Ofereça opções de passeios cobertos ou indoor."
        else:
            chuva = dia.get('chuva_prob', 0)
            if chuva > 70:
                return "Alto risco de chuva. Priorize passeios indoor ou ofereça reagendamento."
            else:
                return "Condições desfavoráveis. Considere descontos ou promoções."
    
    def _get_mock_current_weather(self):
        """Retorna dados mockados quando API não está disponível"""
        return {
            'temperatura': 26.5,
            'sensacao': 28.0,
            'umidade': 75,
            'descricao': 'Parcialmente nublado',
            'icone': '02d',
            'vento': 15.5,
            'visibilidade': 10.0,
            'pressao': 1013,
            'timestamp': datetime.now().isoformat(),
            'mock': True
        }
    
    def _get_mock_forecast(self, days=7):
        """Retorna previsão mockada quando API não está disponível"""
        previsoes = []
        hoje = datetime.now().date()
        
        for i in range(days):
            data = hoje + timedelta(days=i)
            previsoes.append({
                'data': data.isoformat(),
                'temp_min': 22.0 + (i % 3),
                'temp_max': 28.0 + (i % 4),
                'descricao': ['Ensolarado', 'Parcialmente nublado', 'Nublado'][i % 3],
                'icone': ['01d', '02d', '03d'][i % 3],
                'umidade': 70 + (i % 20),
                'chuva_prob': 20 + (i * 10 % 60),
                'vento': 12.0 + (i % 8),
                'mock': True
            })
        
        return previsoes
