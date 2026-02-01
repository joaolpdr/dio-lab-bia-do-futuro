import google.generativeai as genai
import pandas as pd
import json
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class SentinelaAI:
    def __init__(self):
        # Configuração da API
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("A chave GOOGLE_API_KEY não foi encontrada no .env")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Carrega a "Memória" (Base de Conhecimento)
        try:
            self.df_transacoes = pd.read_csv('../data/transacoes.csv')
        except:
            # Fallback caso rode de dentro da pasta src
            self.df_transacoes = pd.read_csv('data/transacoes.csv')

    def _carregar_perfil(self, tipo_perfil):
        """Carrega o JSON do perfil selecionado"""
        caminho = f"../data/perfil_{tipo_perfil}.json"
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
             with open(f"data/perfil_{tipo_perfil}.json", 'r', encoding='utf-8') as f:
                return json.load(f)

    def _analisar_dados(self):
        """Lógica Python pura para processar dados antes do LLM (RAG Simples)"""
        # Filtra transferências internas para não duplicar gastos
        gastos_reais = self.df_transacoes[
            (self.df_transacoes['valor'] < 0) & 
            (self.df_transacoes['tipo'] != 'transferencia')
        ]
        
        total_gasto = gastos_reais['valor'].sum()
        top_gastos = gastos_reais.nsmallest(3, 'valor')[['descricao', 'valor']].to_dict('records')
        
        # Detecção simples de anomalia (duplicidade)
        duplicadas = self.df_transacoes[self.df_transacoes.duplicated(subset=['data', 'descricao', 'valor'], keep=False)]
        alerta_anomalia = ""
        if not duplicadas.empty:
            alerta_anomalia = f"ALERTA: Detectei transações duplicadas: {duplicadas['descricao'].unique()}"
            
        return {
            "total_gasto": total_gasto,
            "top_gastos": top_gastos,
            "alerta": alerta_anomalia
        }

    def gerar_resposta(self, mensagem_usuario, tipo_perfil):
        perfil = self._carregar_perfil(tipo_perfil)
        analise = self._analisar_dados()
        
        # Prompt Engineering Dinâmico
        system_prompt = f"""
        Você é o Sentinela. Aja conforme o perfil abaixo.
        
        --- DADOS DO USUÁRIO ---
        Nome: {perfil['nome']}
        Perfil: {perfil['perfil_financeiro']} (Se 'foco_divida': Seja rígido/amor duro. Se 'foco_reserva': Seja motivador).
        Saldo Atual: R$ {perfil['saldo_atual']}
        
        --- ANÁLISE DO EXTRATO ---
        Total Gasto no Período: R$ {analise['total_gasto']:.2f}
        Maiores Gastos: {analise['top_gastos']}
        {analise['alerta']}
        
        --- PERGUNTA DO USUÁRIO ---
        "{mensagem_usuario}"
        
        Responda de forma curta, direta e usando o tom adequado ao perfil.
        """
        
        response = self.model.generate_content(system_prompt)
        return response.text