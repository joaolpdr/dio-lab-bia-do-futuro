import sqlite3
import pandas as pd
import os

# Caminhos (Configuração automática)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
DB_PATH = os.path.join(DATA_DIR, 'sentinela.db')
CSV_PATH = os.path.join(DATA_DIR, 'transacoes.csv')

def migrar_dados():
    print(f"🔄 Conectando ao banco em: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Garante que existe um usuário dono das transações (ID 1)
    cursor.execute("SELECT id FROM usuarios WHERE id = 1")
    if not cursor.fetchone():
        print("👤 Criando usuário padrão (ID 1) para receber os dados...")
        cursor.execute('''
            INSERT INTO usuarios (id, nome, email, perfil_financeiro, renda_mensal)
            VALUES (1, 'Usuário Importado', 'antigo@sentinela.local', 'equilibrista', 0)
        ''')
        conn.commit()
    
    # 2. Lê o CSV antigo
    if not os.path.exists(CSV_PATH):
        print("❌ Erro: transacoes.csv não encontrado na pasta data.")
        return

    print(f"📂 Lendo arquivo: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    
    # 3. Insere no Banco
    novos_registros = 0
    for _, row in df.iterrows():
        # Verifica duplicidade antes de inserir (para evitar repetir se rodar 2x)
        cursor.execute('''
            SELECT id FROM transacoes 
            WHERE data = ? AND descricao = ? AND valor = ? AND usuario_id = 1
        ''', (str(row['data']), row['descricao'], float(row['valor'])))
        
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO transacoes (usuario_id, data, descricao, categoria, valor, tipo)
                VALUES (1, ?, ?, ?, ?, ?)
            ''', (
                str(row['data']), 
                row['descricao'], 
                row['categoria'], 
                float(row['valor']), 
                row['tipo']
            ))
            novos_registros += 1
            
    conn.commit()
    conn.close()
    
    print(f"✅ Sucesso! {novos_registros} transações foram migradas para o SQLite.")

if __name__ == "__main__":
    migrar_dados()