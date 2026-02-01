from google import genai
from google.genai import errors # Importar para tratar erros específicos
import pandas as pd
import sqlite3
import json
import os
from dotenv import load_dotenv

load_dotenv()

class SentinelaAI:
    def __init__(self):
        # 1. Configuração da API
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("A chave GOOGLE_API_KEY não foi encontrada no .env")
        
        self.client = genai.Client(api_key=api_key)
        
        # 2. Configuração de Caminhos e Banco
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(base_dir, '..', 'data')
        self.db_path = os.path.join(self.data_dir, 'sentinela.db')
        
        # 3. Carrega a Base de Conhecimento
        self.df_transacoes = pd.DataFrame() # Inicializa vazio para evitar erro
        # Carregamento real acontece no gerar_resposta

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _carregar_dados_do_banco(self, usuario_id=1):
        conn = self._get_connection()
        try:
            query = "SELECT * FROM transacoes WHERE usuario_id = ?"
            self.df_transacoes = pd.read_sql_query(query, conn, params=(usuario_id,))
        except Exception as e:
            print(f"Erro ao ler banco: {e}")
            self.df_transacoes = pd.DataFrame(columns=['data','descricao','categoria','valor','tipo'])
        finally:
            conn.close()

    def _salvar_memoria(self, usuario_id, role, content):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_historico (usuario_id, role, content)
            VALUES (?, ?, ?)
        ''', (usuario_id, role, content))
        conn.commit()
        conn.close()

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

        if 'tipo' in self.df_transacoes.columns:
            gastos_reais = self.df_transacoes[
                (self.df_transacoes['valor'] < 0) & 
                (self.df_transacoes['tipo'] != 'transferencia')
            ]
        else:
            gastos_reais = self.df_transacoes[self.df_transacoes['valor'] < 0]
        
        total_gasto = gastos_reais['valor'].sum()
        
        if not gastos_reais.empty:
            top_gastos = gastos_reais.nsmallest(3, 'valor')[['descricao', 'valor']].to_dict('records')
        else:
            top_gastos = []
        
        duplicadas = self.df_transacoes[self.df_transacoes.duplicated(subset=['data', 'descricao', 'valor'], keep=False)]
        alerta = f"ALERTA: Transações duplicadas no histórico: {duplicadas['descricao'].unique().tolist()}" if not duplicadas.empty else ""
            
        return {"total_gasto": total_gasto, "top_gastos": top_gastos, "alerta": alerta}

    def exportar_csv(self):
        if self.df_transacoes.empty: return ""
        cols = [c for c in ['data', 'descricao', 'categoria', 'valor', 'tipo'] if c in self.df_transacoes.columns]
        return self.df_transacoes[cols].to_csv(index=False)

    def gerar_resposta(self, mensagem_usuario, tipo_perfil, dados_extras=None, usuario_id=1):
        self._carregar_dados_do_banco(usuario_id)
        
        perfil = self._carregar_perfil(tipo_perfil)
        analise = self._analisar_dados()
        
        if dados_extras is None: dados_extras = {}

        system_prompt = f"""
        Você é o Sentinela. 
        
        --- PERFIL DO USUÁRIO (ID: {usuario_id}) ---
        Nome: {dados_extras.get('nome', perfil.get('nome', 'Usuário'))}
        Renda Declarada: R$ {dados_extras.get('renda', 'Não informada')}
        Despesas Fixas: {dados_extras.get('fixas', 'Nenhuma')}
        Modo: {perfil.get('perfil_financeiro', 'padrao')}
        
        --- ESTADO FINANCEIRO ---
        Total Gasto Registrado: R$ {analise['total_gasto']:.2f}
        Maiores Gastos: {analise['top_gastos']}
        {analise['alerta']}
        
        --- INSTRUÇÕES ---
        1. Responda de forma curta e prática.
        2. Se o usuário pedir CSV, adicione [DOWNLOAD_CSV].
        3. Se o usuário informar um NOVO gasto, diga que anotou.
        
        --- MENSAGEM ---
        "{mensagem_usuario}"
        """
        
        try:
            # CORREÇÃO PRINCIPAL: Voltamos para o modelo estável 1.5
            response = self.client.models.generate_content(
                model='gemini-1.5-flash',
                contents=system_prompt
            )
            texto_resposta = response.text

            # Salva memória apenas se deu certo a resposta
            self._salvar_memoria(usuario_id, "user", mensagem_usuario)
            self._salvar_memoria(usuario_id, "assistant", texto_resposta)
            
            return texto_resposta

        except errors.ClientError as e:
            # Tratamento específico para erro de cota (429)
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                return "⚠️ **Limite de tráfego atingido.** Estou recebendo muitas mensagens agora. Por favor, aguarde alguns segundos e tente novamente."
            else:
                return f"⚠️ **Erro na conexão:** {e}"
        except Exception as e:
            return f"⚠️ **Erro inesperado:** {e}"