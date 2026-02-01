# Código da Aplicação - Sentinela

Esta pasta contém o código fonte do **Sentinela**, seu guardião financeiro inteligente.

## Estrutura do Projeto

```text
src/
├── app.py              # Interface Principal (Streamlit) com Login e Chat
├── agente.py           # Cérebro do Agente (Integração Gemini, SQL e Pandas)
└── README.md           # Documentação do código

../data/                # Pasta de dados (um nível acima)
├── sentinela.db        # Banco de Dados SQLite (Usuários, Histórico e Transações)
├── transacoes.csv      # Arquivo legado/backup
└── perfil_*.json       # Perfis Comportamentais (Endividado, Equilibrista, Investidor)
```

## Estrutura Sugerida

```text 
src/
├── app.py              # Aplicação principal (Streamlit/Gradio)
├── agente.py           # Lógica do agente
├── config.py           # Configurações (API keys, etc.)
└── requirements.txt    # Dependências
```

## Exemplo de requirements.txt

```text
streamlit       # Interface Web interativa
google-genai    # SDK do Google Gemini (IA Generativa)
pandas          # Manipulação de dados e cálculos financeiros
python-dotenv   # Gerenciamento de variáveis de ambiente (.env)
```

## Como Rodar

```bash
# 1. Instalar as dependências
pip install -r requirements.txt

# 2. Executar a aplicação
streamlit run src/app.py
```
