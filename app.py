import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# =========================
# CONEXÃO FIREBASE (SECRETS)
# =========================

if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))

    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://pizza-app-e6fb5-default-rtdb.firebaseio.com'
    })

# =========================
# INTERFACE
# =========================

st.set_page_config(page_title="Sistema de Pedidos", layout="centered")

st.title("🍕 Sistema de Pedidos")

# INPUTS
nome = st.text_input("Nome do cliente")
sabor = st.text_input("Sabor da pizza")
obs = st.text_input("Observações")

# BOTÃO ENVIAR
if st.button("Enviar Pedido"):
    if nome and sabor:
        pedido = {
            "nome": nome,
            "sabor": sabor,
            "obs": obs
        }

        ref = db.reference('pedidos')
        ref.push(pedido)

        st.success("Pedido enviado!")
    else:
        st.warning("Preencha nome e sabor")

# =========================
# LISTAR PEDIDOS
# =========================

st.divider()
st.subheader("📋 Pedidos em tempo real")

ref = db.reference('pedidos')
dados = ref.get()

if dados:
    pedidos_lista = list(dados.values())

    # mostra do mais recente pro mais antigo
    pedidos_lista.reverse()

    for i, pedido in enumerate(pedidos_lista):
        st.markdown(f"""
        ### Pedido {i+1}
        👤 **Cliente:** {pedido.get('nome', '')}  
        🍕 **Sabor:** {pedido.get('sabor', '')}  
        📝 **Obs:** {pedido.get('obs', '')}
        """)
        st.divider()
else:
    st.info("Nenhum pedido ainda")

# =========================
# BOTÃO ATUALIZAR
# =========================

if st.button("🔄 Atualizar pedidos"):
    st.rerun()
