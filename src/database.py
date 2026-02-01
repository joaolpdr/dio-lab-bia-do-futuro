import sqlite3
import os

# Define o caminho do banco (ficará na pasta data)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'sentinela.db')

def get_connection():
    """Retorna conexão com o banco"""
    return sqlite3.connect(DB_PATH)

def inicializar_banco():
    """Cria as tabelas se não existirem"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Tabela Usuários
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE,
        perfil_financeiro TEXT DEFAULT 'equilibrista',
        renda_mensal REAL DEFAULT 0.0,
        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 2. Tabela Transações (Espelho do CSV)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        data DATE,
        descricao TEXT,
        categoria TEXT,
        valor REAL,
        tipo TEXT,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )
    ''')
    
    # 3. Tabela de Recorrências (Contas Fixas)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recorrencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        descricao TEXT,
        valor_estimado REAL,
        dia_vencimento INTEGER,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )
    ''')

    # 4. Histórico de Chat (Memória de Longo Prazo)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_historico (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        role TEXT,
        content TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Banco de dados inicializado em: {DB_PATH}")

if __name__ == "__main__":
    inicializar_banco()