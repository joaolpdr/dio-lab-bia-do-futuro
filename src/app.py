import streamlit as st
import sqlite3
import os
from agente import SentinelaAI
import time

# --- Configuração de Caminhos ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'data', 'sentinela.db')

def get_usuario_id(nome, email, renda=0, perfil='equilibrista'):
    """Busca o usuário no banco ou cria um novo"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tenta achar pelo email
    cursor.execute("SELECT id, perfil_financeiro, renda_mensal FROM usuarios WHERE email = ?", (email,))
    data = cursor.fetchone()
    
    if data:
        conn.close()
        return data[0], data[1], data[2] # Retorna ID, Perfil, Renda
    else:
        # Cria novo usuário
        cursor.execute('''
            INSERT INTO usuarios (nome, email, perfil_financeiro, renda_mensal)
            VALUES (?, ?, ?, ?)
        ''', (nome, email, perfil, renda))
        conn.commit()
        novo_id = cursor.lastrowid
        conn.close()
        return novo_id, perfil, renda

# --- Configuração da Página ---
st.set_page_config(page_title="Sentinela Financeiro", page_icon="🛡️")

# --- Inicialização do Estado ---
if "setup_completo" not in st.session_state:
    st.session_state.setup_completo = False
if "usuario_id" not in st.session_state:
    st.session_state.usuario_id = None
if "dados_usuario" not in st.session_state:
    st.session_state.dados_usuario = {}
if "perfil_usuario" not in st.session_state:
    st.session_state.perfil_usuario = "equilibrista"
if "agente" not in st.session_state:
    st.session_state.agente = SentinelaAI()
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🛡️ Sentinela: Seu Guardião Financeiro")

# --- ONBOARDING / LOGIN ---
if not st.session_state.setup_completo:
    st.markdown("### 👋 Bem-vindo ao Sentinela")
    st.info("Entre com seus dados para carregar seu perfil exclusivo.")
    
    with st.form("form_login"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Seu Nome")
            email = st.text_input("Seu E-mail (Chave de Acesso)")
        with col2:
            renda = st.number_input("Renda Mensal (R$)", min_value=0.0, step=100.0)
            
        st.markdown("---")
        
        # [CORREÇÃO FINAL] Removemos o checkbox bugado. A caixa aparece sempre.
        st.markdown("**Despesas Fixas (Opcional)**")
        st.caption("Liste contas como Aluguel, Internet, Luz, etc.")
        despesas_fixas = st.text_area(
            "Lista de Despesas:", 
            placeholder="Ex: Aluguel 1200, Luz 150, Internet 100...",
            height=100
        )

        st.markdown("---")
        situacao = st.radio("Qual sua situação atual?", [
            "🚨 Tenho dívidas e contas atrasadas (Foco em Quitar)",
            "⚖️ Pago as contas, mas não sobra nada (Foco em Controle)",
            "💰 Tenho dinheiro sobrando (Foco em Investir)"
        ])
        
        submit = st.form_submit_button("🚀 Acessar Minha Conta")

        if submit and nome and email:
            perfil_selecionado = "equilibrista"
            if "dívidas" in situacao: perfil_selecionado = "endividado"
            elif "Investir" in situacao: perfil_selecionado = "investidor"
            
            # Garante que, se estiver vazio, passamos um texto padrão
            fixas_texto = despesas_fixas if despesas_fixas.strip() else "Nenhuma informada"

            # Busca/Cria no banco
            u_id, u_perfil, u_renda = get_usuario_id(nome, email, renda, perfil_selecionado)
            
            # Salva na Sessão
            st.session_state.usuario_id = u_id
            st.session_state.perfil_usuario = u_perfil
            
            st.session_state.dados_usuario = {
                "nome": nome, 
                "renda": u_renda,
                "fixas": fixas_texto
            }
            
            st.session_state.setup_completo = True
            
            msg_sistema = f"**Sistema:** Identificado Usuário #{u_id} ({nome}). Perfil: {u_perfil.upper()}"
            st.session_state.messages.append({"role": "assistant", "content": msg_sistema})
            st.rerun()

# --- CHAT ---
else:
    st.sidebar.header(f"👤 Olá, {st.session_state.dados_usuario.get('nome')}")
    st.sidebar.caption(f"ID do Usuário: {st.session_state.usuario_id}")
    st.sidebar.text(f"Renda: R$ {st.session_state.dados_usuario.get('renda'):.2f}")
    st.sidebar.info(f"Modo: **{st.session_state.perfil_usuario.upper()}**")
    
    if st.sidebar.button("Sair / Trocar Usuário"):
        st.session_state.clear()
        st.rerun()

    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("show_download"):
                csv_data = st.session_state.agente.exportar_csv() 
                st.download_button("📥 Baixar CSV", csv_data, "extrato.csv", "text/csv", key=f"dl_{i}")

    if len(st.session_state.messages) == 1:
        with st.spinner("Analisando seu perfil..."):
            
            prompt_inicial = f"""
            Acabei de entrar. 
            Minha renda é R$ {st.session_state.dados_usuario['renda']}.
            Minhas despesas fixas são: {st.session_state.dados_usuario['fixas']}.
            
            O banco de dados ainda está vazio pois sou novo.
            
            Por favor:
            1. Me dê as boas vindas pelo nome.
            2. Confirme que entendeu minha renda e minhas despesas fixas (calcule quanto sobra, se possível).
            3. Pergunte qual foi meu último gasto variável para começarmos.
            """
            
            boas_vindas = st.session_state.agente.gerar_resposta(
                prompt_inicial, 
                st.session_state.perfil_usuario,
                st.session_state.dados_usuario,
                usuario_id=st.session_state.usuario_id
            )
            st.session_state.messages.append({"role": "assistant", "content": boas_vindas})
            st.rerun()

    if prompt := st.chat_input("Digite sua mensagem..."):
        st.chat_message("user").write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Processando..."):
            time.sleep(1)
            resposta = st.session_state.agente.gerar_resposta(
                prompt, 
                st.session_state.perfil_usuario,
                st.session_state.dados_usuario,
                usuario_id=st.session_state.usuario_id
            )
            
            mostrar_botao = "[DOWNLOAD_CSV]" in resposta
            texto_limpo = resposta.replace("[DOWNLOAD_CSV]", "")
        
        st.chat_message("assistant").write(texto_limpo)
        
        if mostrar_botao:
            csv_data = st.session_state.agente.exportar_csv()
            st.download_button("📥 Baixar Extrato", csv_data, "extrato.csv", "text/csv", key="dl_now")
            
        st.session_state.messages.append({
            "role": "assistant", 
            "content": texto_limpo, 
            "show_download": mostrar_botao
        })