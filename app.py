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
import time
from datetime import datetime, timedelta

st.subheader("🔥 Fila de Produção")

ref = db.reference('pedidos')
dados = ref.get()

if dados:
    pedidos_lista = list(dados.items())  # pega chave + valor

    # ordenar por ordem de chegada
    pedidos_lista = sorted(pedidos_lista, key=lambda x: x[0])

    agora = datetime.utcnow()

    for i, (key, pedido) in enumerate(pedidos_lista):

        tempo_preparo = 15 + (i * 10)

        # cria timestamp se não existir
        if "inicio" not in pedido:
            inicio = datetime.utcnow().timestamp()
            db.reference(f'pedidos/{key}/inicio').set(inicio)
        else:
            inicio = datetime.fromtimestamp(pedido["inicio"])

        fim = inicio + timedelta(minutes=tempo_preparo)
        restante = fim - agora

        minutos = int(restante.total_seconds() // 60)
        segundos = int(restante.total_seconds() % 60)

        if restante.total_seconds() <= 0:
            status = "✅ Pronto"
        else:
            status = f"⏳ {minutos}m {segundos}s"

        st.markdown(f"""
        ### 🍕 Pedido {i+1}
        👤 {pedido.get('nome', '')}  
        🍕 {pedido.get('sabor', '')}  
        📝 {pedido.get('obs', '')}  

        ⏱️ Tempo: {tempo_preparo} min  
        🔥 Status: {status}
        """)

        # BOTÃO FINALIZAR
        if st.button(f"Finalizar Pedido {i+1}"):
            db.reference(f'pedidos/{key}').delete()
            st.rerun()

        st.divider()

else:
    st.info("Sem pedidos")

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
