from google import genai
import pandas as pd
import json
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class SentinelaAI:
    def __init__(self):
        # 1. Configuração da API
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("A chave GOOGLE_API_KEY não foi encontrada no .env")
        
        self.client = genai.Client(api_key=api_key)
        
        # 2. Configuração de Caminhos (A Mágica acontece aqui)
        # Pega o diretório onde este arquivo (agente.py) está: .../src
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Define o caminho da pasta data: .../src/../data (que vira .../data)
        self.data_dir = os.path.join(base_dir, '..', 'data')
        
        # Caminho do CSV
        csv_path = os.path.join(self.data_dir, 'transacoes.csv')

        # 3. Carrega a Base de Conhecimento (CSV)
        try:
            self.df_transacoes = pd.read_csv(csv_path)
        except FileNotFoundError:
            # Cria um dataframe vazio para não quebrar o app se o CSV sumir
            print(f"ERRO: Arquivo não encontrado em {csv_path}")
            self.df_transacoes = pd.DataFrame(columns=['data','descricao','categoria','valor','tipo'])

    def _carregar_perfil(self, tipo_perfil):
        """Carrega o JSON usando caminho absoluto"""
        filename = f"perfil_{tipo_perfil}.json"
        caminho_arquivo = os.path.join(self.data_dir, filename)
        
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Retorna um perfil de emergência caso o arquivo não exista
            return {
                "nome": "Usuário (Perfil Não Encontrado)",
                "perfil_financeiro": "padrao",
                "saldo_atual": 0.0
            }

    def _analisar_dados(self):
        """Lógica Python pura para processar dados"""
        if self.df_transacoes.empty:
            return {"total_gasto": 0, "top_gastos": [], "alerta": ""}

        if 'tipo' in self.df_transacoes.columns:
            gastos_reais = self.df_transacoes[
                (self.df_transacoes['valor'] < 0) & 
                (self.df_transacoes['tipo'] != 'transferencia')
            ]
        else:
            gastos_reais = self.df_transacoes[self.df_transacoes['valor'] < 0]
        
        total_gasto = gastos_reais['valor'].sum()
        top_gastos = gastos_reais.nsmallest(3, 'valor')[['descricao', 'valor']].to_dict('records')
        
        duplicadas = self.df_transacoes[self.df_transacoes.duplicated(subset=['data', 'descricao', 'valor'], keep=False)]
        alerta_anomalia = ""
        if not duplicadas.empty:
            lista = duplicadas['descricao'].unique().tolist()
            alerta_anomalia = f"ALERTA: Detectei transações duplicadas: {lista}"
            
        return {
            "total_gasto": total_gasto,
            "top_gastos": top_gastos,
            "alerta": alerta_anomalia
        }

    def gerar_resposta(self, mensagem_usuario, tipo_perfil):
        perfil = self._carregar_perfil(tipo_perfil)
        analise = self._analisar_dados()
        
        # System Prompt Atualizado com o Perfil Equilibrista
        system_prompt = f"""
        Você é o Sentinela. Aja conforme o perfil abaixo.
        
        --- DADOS DO USUÁRIO ---
        Nome: {perfil.get('nome', 'Usuário')}
        Perfil: {perfil.get('perfil_financeiro', 'padrao')} 
        
        DIRETRIZES DE TOM:
        - Se 'foco_divida': Seja rígido, estilo "amor duro".
        - Se 'foco_reserva': Seja motivador e celebre investimentos.
        - Se 'foco_controle': Seja cauteloso e prático (Alerta de risco/Equilibrista).
        
        Saldo Atual: R$ {perfil.get('saldo_atual', 0)}
        
        --- ANÁLISE DO EXTRATO ---
        Total Gasto no Período: R$ {analise['total_gasto']:.2f}
        Maiores Gastos: {analise['top_gastos']}
        {analise['alerta']}
        
        --- PERGUNTA DO USUÁRIO ---
        "{mensagem_usuario}"
        
        Responda de forma curta, direta e usando o tom adequado ao perfil.
        """
        
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=system_prompt
        )
        
        return response.text