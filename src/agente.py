from google import genai
import pandas as pd
import json
import os
from dotenv import load_dotenv

load_dotenv()

class SentinelaAI:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("A chave GOOGLE_API_KEY não foi encontrada no .env")
        
        self.client = genai.Client(api_key=api_key)
        
        # Configuração de Caminhos
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(base_dir, '..', 'data')
        csv_path = os.path.join(self.data_dir, 'transacoes.csv')

        try:
            self.df_transacoes = pd.read_csv(csv_path)
        except FileNotFoundError:
            self.df_transacoes = pd.DataFrame(columns=['data','descricao','categoria','valor','tipo'])

    def _carregar_perfil(self, tipo_perfil):
        filename = f"perfil_{tipo_perfil}.json"
        caminho_arquivo = os.path.join(self.data_dir, filename)
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"nome": "Usuário", "perfil_financeiro": "padrao", "saldo_atual": 0.0}

    def _analisar_dados(self):
        if self.df_transacoes.empty:
            return {"total_gasto": 0, "top_gastos": [], "alerta": ""}

        # Garante tratamento de erros caso colunas mudem
        if 'tipo' in self.df_transacoes.columns:
            gastos_reais = self.df_transacoes[
                (self.df_transacoes['valor'] < 0) & 
                (self.df_transacoes['tipo'] != 'transferencia')
            ]
        else:
            gastos_reais = self.df_transacoes[self.df_transacoes['valor'] < 0]
        
        total_gasto = gastos_reais['valor'].sum()
        
        # Pega Top Gastos apenas se houver dados
        if not gastos_reais.empty:
            top_gastos = gastos_reais.nsmallest(3, 'valor')[['descricao', 'valor']].to_dict('records')
        else:
            top_gastos = []
        
        duplicadas = self.df_transacoes[self.df_transacoes.duplicated(subset=['data', 'descricao', 'valor'], keep=False)]
        alerta = f"ALERTA (CSV Antigo): Transações duplicadas detectadas no histórico: {duplicadas['descricao'].unique().tolist()}" if not duplicadas.empty else ""
            
        return {"total_gasto": total_gasto, "top_gastos": top_gastos, "alerta": alerta}

    def exportar_csv(self):
        if self.df_transacoes.empty: return ""
        cols = [c for c in ['data', 'descricao', 'categoria', 'valor', 'tipo'] if c in self.df_transacoes.columns]
        return self.df_transacoes[cols].to_csv(index=False)

    def gerar_resposta(self, mensagem_usuario, tipo_perfil, dados_extras=None):
        perfil = self._carregar_perfil(tipo_perfil)
        analise = self._analisar_dados()
        
        if dados_extras is None: dados_extras = {}

        # PROMPT DE COMPORTAMENTO REFINADO
        system_prompt = f"""
        Você é o Sentinela, um consultor financeiro pessoal.
        
        --- SEU CONTEXTO ATUAL ---
        O usuário acabou de preencher um formulário de onboarding.
        Nome: {dados_extras.get('nome', perfil.get('nome', 'Usuário'))}
        Renda Declarada Agora: R$ {dados_extras.get('renda', '0.00')}
        Despesas Fixas Declaradas: {dados_extras.get('fixas', 'Não informadas')}
        Perfil Comportamental: {perfil.get('perfil_financeiro', 'padrao')}
        
        --- DADOS DO ARQUIVO CSV (HISTÓRICO) ---
        (Atenção: Estes dados podem ser antigos ou estar desatualizados em relação à renda declarada acima)
        Total de Gastos Registrados: R$ {analise['total_gasto']:.2f}
        Maiores Gastos: {analise['top_gastos']}
        {analise['alerta']}
        
        --- DIRETRIZES DE PERSONALIDADE ---
        1. PRIORIDADE ZERO: Use a 'Renda Declarada Agora' como verdade absoluta. Se o CSV mostrar saldo 0 ou negativo, assuma que o CSV está desatualizado e PRECISAS ser preenchido.
        2. NÃO VOMITE NÚMEROS: Não comece listando gastos do CSV (como Apple Services) a menos que o usuário pergunte especificamente sobre o histórico.
        3. TOM DE VOZ:
           - 'endividado': Amor duro. Foco em parar de gastar.
           - 'equilibrista': Prático. Foco em organizar para sobrar.
           - 'investidor': Estratégico. Foco em rentabilidade.
        
        --- FORMATO DE RESPOSTA ---
        - Sempre que pedir para adicionar um gasto, mostre o modelo:
          "💡 *Exemplo:* `50.00 - Pizza - Lazer`"
        - Se o usuário pedir CSV/Planilha, adicione [DOWNLOAD_CSV] no final.
        
        --- INSTRUÇÃO PARA ESTA MENSAGEM ---
        O usuário disse: "{mensagem_usuario}"
        
        Se a mensagem do usuário for curta (tipo "Oi", "Vamos", "Claro"), ignore o CSV antigo e faça o onboarding:
        1. Confirme que entendeu a renda de R$ {dados_extras.get('renda')}.
        2. Confirme as despesas fixas.
        3. Pergunte quais são os gastos variáveis recentes para começar a popular a planilha nova.
        """
        
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=system_prompt
        )
        
        return response.text