import streamlit as st
from agente import SentinelaAI

# Configuração da Página
st.set_page_config(page_title="Sentinela Financeiro", page_icon="🫡")

st.title("🫡 Sentinela: Seu Guardião Financeiro")

# Inicializa o Agente
if "agente" not in st.session_state:
    try:
        st.session_state.agente = SentinelaAI()
    except Exception as e:
        st.error(f"Erro ao iniciar o agente. Verifique a API KEY. Detalhes: {e}")
        st.stop()

# Sidebar para Simulação de Contexto (Debug)
st.sidebar.header("⚙️ Simulação de Persona")
tipo_perfil = st.sidebar.selectbox(
    "Quem está usando agora?",
    ("endividado", "investidor", "equilibrista")
)

st.sidebar.info(
    "Mude o perfil acima para testar como o Sentinela muda o tom de voz (Rígido vs Motivador)."
)

# Histórico do Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Renderiza mensagens anteriores
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input do Usuário
if prompt := st.chat_input("Pergunte sobre suas finanças..."):
    # 1. Mostra msg do usuário
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Gera resposta do Sentinela
    with st.spinner("Analisando seus dados..."):
        resposta = st.session_state.agente.gerar_resposta(prompt, tipo_perfil)
    
    # 3. Mostra resposta do Agente
    st.chat_message("assistant").write(resposta)
    st.session_state.messages.append({"role": "assistant", "content": resposta})