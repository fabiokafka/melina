"""
Serviço de integração com OpenAI para funcionalidades de IA
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    def gerar_campanha_email(self, clientes_data, objetivo):
        """
        Gera conteúdo de campanha de email marketing usando IA
        
        Args:
            clientes_data: Dados dos clientes alvo
            objetivo: Objetivo da campanha
        """
        try:
            prompt = f"""
            Crie uma campanha de email marketing para a Maremar Turismo em Ilhabela.
            
            Objetivo: {objetivo}
            
            Informações sobre os clientes:
            {clientes_data}
            
            Por favor, gere:
            1. Assunto do email (atraente e que gere curiosidade)
            2. Corpo do email (personalizado, persuasivo e com call-to-action)
            3. Sugestões de segmentação
            
            Formato: JSON com as chaves "assunto", "corpo", "segmentacao"
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um especialista em marketing turístico e copywriting."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Erro ao gerar campanha de email: {str(e)}")
            raise
    
    def gerar_campanha_whatsapp(self, clientes_data, objetivo):
        """
        Gera conteúdo de campanha de WhatsApp usando IA
        
        Args:
            clientes_data: Dados dos clientes alvo
            objetivo: Objetivo da campanha
        """
        try:
            prompt = f"""
            Crie mensagens de WhatsApp para campanha da Maremar Turismo em Ilhabela.
            
            Objetivo: {objetivo}
            
            Informações sobre os clientes:
            {clientes_data}
            
            Por favor, gere:
            1. Mensagem principal (curta, direta e com emoji apropriado)
            2. Variações da mensagem para diferentes perfis
            3. Sugestões de horário de envio
            
            Formato: JSON com as chaves "mensagem_principal", "variacoes", "horarios_sugeridos"
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um especialista em marketing turístico e comunicação via WhatsApp."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Erro ao gerar campanha de WhatsApp: {str(e)}")
            raise
    
    def analisar_vendas(self, vendas_data):
        """
        Analisa dados de vendas e gera insights usando IA
        
        Args:
            vendas_data: Dados de vendas para análise
        """
        try:
            prompt = f"""
            Analise os seguintes dados de vendas da Maremar Turismo:
            
            {vendas_data}
            
            Por favor, forneça:
            1. Principais insights sobre o desempenho
            2. Tendências identificadas
            3. Recomendações para aumentar as vendas
            4. Passeios com melhor performance
            5. Oportunidades de melhoria
            
            Formato: JSON estruturado
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um analista de dados especializado em turismo."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Erro ao analisar vendas: {str(e)}")
            raise
    
    def prever_impacto_clima(self, clima_data, passeios_data):
        """
        Prevê o impacto do clima nas vendas de passeios
        
        Args:
            clima_data: Dados climáticos
            passeios_data: Dados dos passeios
        """
        try:
            prompt = f"""
            Com base nas seguintes informações climáticas e de passeios da Maremar Turismo:
            
            Clima: {clima_data}
            Passeios: {passeios_data}
            
            Por favor, forneça:
            1. Previsão de impacto do clima em cada passeio
            2. Recomendações de ajuste de preços ou promoções
            3. Sugestões de comunicação com clientes
            4. Passeios mais adequados para as condições previstas
            
            Formato: JSON estruturado
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um especialista em turismo e análise de impacto climático em vendas."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Erro ao prever impacto do clima: {str(e)}")
            raise
    
    def pesquisar_baleias_ilhabela(self):
        """
        Pesquisa e compila informações sobre baleias em Ilhabela
        """
        try:
            prompt = """
            Compile informações detalhadas sobre baleias em Ilhabela, SP, Brasil.
            
            Inclua:
            1. Espécies de baleias que aparecem na região
            2. Melhor época para avistamento
            3. Rotas migratórias
            4. Dados estatísticos de avistamentos
            5. Curiosidades e informações educacionais
            6. Importância ecológica
            
            Formato: JSON estruturado com dados organizados
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um biólogo marinho especializado em cetáceos e turismo de observação."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Erro ao pesquisar sobre baleias: {str(e)}")
            raise
    
    def analisar_campanhas_marketing(self, google_ads_data, meta_ads_data):
        """
        Analisa campanhas de marketing e sugere melhorias
        
        Args:
            google_ads_data: Dados de campanhas do Google Ads
            meta_ads_data: Dados de campanhas do Meta Ads
        """
        try:
            prompt = f"""
            Analise as seguintes campanhas de marketing da Maremar Turismo:
            
            Google Ads: {google_ads_data}
            Meta Ads: {meta_ads_data}
            
            Por favor, forneça:
            1. Análise de performance de cada campanha
            2. Comparação entre plataformas
            3. ROI e métricas principais
            4. Sugestões de otimização
            5. Recomendações de budget
            6. Novos públicos-alvo sugeridos
            7. Ideias de criativos e copy
            
            Formato: JSON estruturado
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um especialista em marketing digital e performance de campanhas pagas."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Erro ao analisar campanhas de marketing: {str(e)}")
            raise
