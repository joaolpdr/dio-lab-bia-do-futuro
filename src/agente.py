from google import genai
import pandas as pd
import json
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class SentinelaAI:
    def __init__(self):
        # Configuração da API (Nova SDK)
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("A chave GOOGLE_API_KEY não foi encontrada no .env")
        
        # Na nova versão, instanciamos um Client
        self.client = genai.Client(api_key=api_key)
        
        # Carrega a "Memória" (Base de Conhecimento)
        try:
            # Tenta carregar relativo à pasta src
            self.df_transacoes = pd.read_csv('../data/transacoes.csv')
        except FileNotFoundError:
            # Fallback caso rode de dentro da raiz
            self.df_transacoes = pd.read_csv('data/transacoes.csv')

    def _carregar_perfil(self, tipo_perfil):
        """Carrega o JSON do perfil selecionado"""
        filename = f"perfil_{tipo_perfil}.json"
        try:
            with open(f"../data/{filename}", 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            with open(f"data/{filename}", 'r', encoding='utf-8') as f:
                return json.load(f)

    def _analisar_dados(self):
        """Lógica Python pura para processar dados antes do LLM"""
        # Filtra transferências internas para não duplicar gastos
        # Verifica se a coluna 'tipo' existe, se não, assume tudo como gasto para evitar erro
        if 'tipo' in self.df_transacoes.columns:
            gastos_reais = self.df_transacoes[
                (self.df_transacoes['valor'] < 0) & 
                (self.df_transacoes['tipo'] != 'transferencia')
            ]
        else:
            gastos_reais = self.df_transacoes[self.df_transacoes['valor'] < 0]
        
        total_gasto = gastos_reais['valor'].sum()
        
        # Pega os Top 3 gastos
        top_gastos = gastos_reais.nsmallest(3, 'valor')[['descricao', 'valor']].to_dict('records')
        
        # Detecção simples de anomalia (duplicidade)
        duplicadas = self.df_transacoes[self.df_transacoes.duplicated(subset=['data', 'descricao', 'valor'], keep=False)]
        alerta_anomalia = ""
        if not duplicadas.empty:
            lista_duplicadas = duplicadas['descricao'].unique().tolist()
            alerta_anomalia = f"ALERTA: Detectei transações duplicadas: {lista_duplicadas}"
            
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
        Nome: {perfil.get('nome', 'Usuário')}
        Perfil: {perfil.get('perfil_financeiro', 'padrao')} 
        (Se 'foco_divida': Seja rígido/amor duro. Se 'foco_reserva': Seja motivador).
        Saldo Atual: R$ {perfil.get('saldo_atual', 0)}
        
        --- ANÁLISE DO EXTRATO ---
        Total Gasto no Período: R$ {analise['total_gasto']:.2f}
        Maiores Gastos: {analise['top_gastos']}
        {analise['alerta']}
        
        --- PERGUNTA DO USUÁRIO ---
        "{mensagem_usuario}"
        
        Responda de forma curta, direta e usando o tom adequado ao perfil.
        """
        
        # Chamada Nova API (generate_content agora é via client.models)
        response = self.client.models.generate_content(
            model='gemini-1.5-flash',
            contents=system_prompt
        )
        
        return response.text