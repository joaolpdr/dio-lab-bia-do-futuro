import streamlit as st
from agente import SentinelaAI
import time

# --- Configuração da Página ---
st.set_page_config(page_title="Sentinela Financeiro", page_icon="🛡️")

# --- Inicialização do Estado (Session State) ---
if "setup_completo" not in st.session_state:
    st.session_state.setup_completo = False

if "perfil_usuario" not in st.session_state:
    st.session_state.perfil_usuario = "equilibrista" # Padrão

if "agente" not in st.session_state:
    st.session_state.agente = SentinelaAI()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Título ---
st.title("🛡️ Sentinela: Seu Guardião Financeiro")

# --- LÓGICA DO ONBOARDING (Formulário Inicial) ---
if not st.session_state.setup_completo:
    st.markdown("""
    ### 👋 Olá! Eu sou o Sentinela.
    Antes de começarmos, preciso entender seu momento financeiro atual para te ajudar melhor.
    """)
    
    with st.form("form_onboarding"):
        nome = st.text_input("Como você gostaria de ser chamado?")
        
        situacao = st.radio(
            "Qual frase define melhor sua situação atual?",
            [
                "🚨 Tenho dívidas e contas atrasadas.",
                "⚖️ Pago as contas, mas não sobra quase nada.",
                "💰 Tenho dinheiro sobrando e quero investir."
            ]
        )
        
        submit = st.form_submit_button("Iniciar Jornada")

        if submit and nome:
            # Lógica simples de classificação de perfil
            perfil_detectado = "equilibrista"
            msg_inicial = ""
            
            if "dívidas" in situacao:
                perfil_detectado = "endividado"
                msg_inicial = f"Opa, {nome}. Entendido. Vamos priorizar apagar esse incêndio das dívidas. O que está te preocupando mais hoje?"
            elif "sobra quase nada" in situacao:
                perfil_detectado = "equilibrista"
                msg_inicial = f"Prazer, {nome}. Vamos trabalhar para organizar esse fluxo e fazer sobrar dinheiro. Vamos analisar seus gastos?"
            else:
                perfil_detectado = "investidor"
                msg_inicial = f"Excelente, {nome}! Hora de fazer o dinheiro trabalhar. Vamos olhar as melhores oportunidades para você."
            
            # Salva no estado
            st.session_state.perfil_usuario = perfil_detectado
            st.session_state.setup_completo = True
            
            # Adiciona a primeira mensagem do Bot automaticamente
            st.session_state.messages.append({"role": "assistant", "content": msg_inicial})
            
            # Recarrega a página para sumir com o formulário e mostrar o chat
            st.rerun()

# --- LÓGICA DO CHAT (Só aparece depois do formulário) ---
else:
    # Sidebar Informativa (Mostra o perfil que foi definido)
    st.sidebar.header("👤 Perfil Detectado")
    st.sidebar.info(f"Modo: **{st.session_state.perfil_usuario.upper()}**")
    
    if st.sidebar.button("Reiniciar Conversa"):
        st.session_state.setup_completo = False
        st.session_state.messages = []
        st.rerun()

    # Renderiza mensagens anteriores
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input do Usuário
    if prompt := st.chat_input("Digite sua mensagem..."):
        # 1. Mostra msg do usuário
        st.chat_message("user").write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 2. Gera resposta do Sentinela
        with st.spinner("Analisando..."):
            # Delay fake para parecer mais natural
            time.sleep(1)
            resposta = st.session_state.agente.gerar_resposta(prompt, st.session_state.perfil_usuario)
        
        # 3. Mostra resposta do Agente
        st.chat_message("assistant").write(resposta)
        st.session_state.messages.append({"role": "assistant", "content": resposta})