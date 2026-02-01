import streamlit as st
from agente import SentinelaAI
import time

st.set_page_config(page_title="Sentinela Financeiro", page_icon="🛡️")

if "setup_completo" not in st.session_state:
    st.session_state.setup_completo = False
if "dados_usuario" not in st.session_state:
    st.session_state.dados_usuario = {}
if "perfil_usuario" not in st.session_state:
    st.session_state.perfil_usuario = "equilibrista"
if "agente" not in st.session_state:
    st.session_state.agente = SentinelaAI()
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🛡️ Sentinela: Seu Guardião Financeiro")

# --- ONBOARDING ---
if not st.session_state.setup_completo:
    st.markdown("### 👋 Olá! Vamos configurar seu perfil.")
    st.info("Responda com sinceridade para eu calibrar minhas recomendações.")
    
    with st.form("form_onboarding"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Seu Nome")
        with col2:
            renda = st.number_input("Renda Mensal Líquida (R$)", min_value=0.0, step=100.0)
            
        st.markdown("---")
        situacao = st.radio("Qual sua situação atual?", [
            "🚨 Tenho dívidas e contas atrasadas (Foco em Quitar)",
            "⚖️ Pago as contas, mas não sobra nada (Foco em Controle)",
            "💰 Tenho dinheiro sobrando (Foco em Investir)"
        ])
        
        st.markdown("---")
        tem_fixas = st.checkbox("Já possuo despesas fixas recorrentes?")
        despesas_fixas = st.text_area(
            "Quais são? (Opcional)", 
            placeholder="Ex: Aluguel R$ 1200, Internet R$ 100...",
        ) if tem_fixas else ""

        submit = st.form_submit_button("🚀 Iniciar Sentinela")

        if submit and nome:
            if "dívidas" in situacao:
                perfil = "endividado"
            elif "sobra nada" in situacao:
                perfil = "equilibrista"
            else:
                perfil = "investidor"
            
            # Salva dados
            st.session_state.perfil_usuario = perfil
            st.session_state.dados_usuario = {
                "nome": nome,
                "renda": renda,
                "fixas": despesas_fixas if despesas_fixas else "Nenhuma informada"
            }
            
            # MENSAGEM INICIAL MAIS INTELIGENTE
            # Não tentamos adivinhar a resposta aqui. Deixamos uma mensagem de "Sistema"
            # para o usuário saber que deu certo, e induzimos o "Olá" para o bot pegar o contexto.
            
            msg_sistema = f"**Sistema:** Perfil de {nome} configurado! Renda: R$ {renda} | Modo: {perfil.upper()}"
            st.session_state.messages.append({"role": "assistant", "content": msg_sistema, "show_download": False})
            
            st.session_state.setup_completo = True
            st.rerun()

# --- CHAT ---
else:
    st.sidebar.header("👤 Dados do Usuário")
    st.sidebar.text(f"Nome: {st.session_state.dados_usuario.get('nome')}")
    st.sidebar.text(f"Renda: R$ {st.session_state.dados_usuario.get('renda'):.2f}")
    st.sidebar.info(f"Modo: **{st.session_state.perfil_usuario.upper()}**")
    
    if st.sidebar.button("Reiniciar Conversa"):
        st.session_state.setup_completo = False
        st.session_state.messages = []
        st.session_state.dados_usuario = {}
        st.rerun()

    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("show_download"):
                csv_data = st.session_state.agente.exportar_csv()
                st.download_button(
                    label="📥 Baixar Extrato CSV",
                    data=csv_data,
                    file_name="extrato.csv",
                    mime="text/csv",
                    key=f"dl_{i}"
                )

    # Se for a primeira vez que entra aqui (só tem a msg do sistema), 
    # forçamos o usuário a dar o "Olá" ou o Bot a se apresentar?
    # Melhor: O Bot se apresenta automaticamente baseada no contexto.
    if len(st.session_state.messages) == 1:
        with st.spinner("Iniciando consultoria..."):
            # Chamamos o agente com um prompt "fake" de início para ele se apresentar
            boas_vindas = st.session_state.agente.gerar_resposta(
                "Acabei de preencher meu cadastro. Me dê as boas vindas e confirme meus dados.", 
                st.session_state.perfil_usuario,
                st.session_state.dados_usuario
            )
            st.session_state.messages.append({"role": "assistant", "content": boas_vindas, "show_download": False})
            st.rerun()

    if prompt := st.chat_input("Digite sua mensagem..."):
        st.chat_message("user").write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Pensando..."):
            time.sleep(1)
            resposta_bruta = st.session_state.agente.gerar_resposta(
                prompt, 
                st.session_state.perfil_usuario,
                st.session_state.dados_usuario
            )
            
            mostrar_botao = "[DOWNLOAD_CSV]" in resposta_bruta
            texto_limpo = resposta_bruta.replace("[DOWNLOAD_CSV]", "")
        
        st.chat_message("assistant").write(texto_limpo)
        
        if mostrar_botao:
            csv_data = st.session_state.agente.exportar_csv()
            st.download_button("📥 Baixar Extrato", csv_data, "extrato.csv", "text/csv", key="dl_now")
            
        st.session_state.messages.append({
            "role": "assistant", 
            "content": texto_limpo, 
            "show_download": mostrar_botao
        })