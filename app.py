import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, timedelta

# =========================
# AUTO REFRESH
# =========================
st.autorefresh(interval=2000, key="refresh")

# =========================
# FIREBASE
# =========================
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://pizza-app-e6fb5-default-rtdb.firebaseio.com'
    })

# =========================
# MODO
# =========================
st.title("🍕 Sistema de Pedidos")

modo = st.radio("Modo", ["Atendente", "Cozinha"])

# =========================
# MODO ATENDENTE
# =========================
if modo == "Atendente":

    st.subheader("📝 Novo Pedido")

    nome = st.text_input("Nome do cliente")
    sabor = st.text_input("Sabor da pizza")
    obs = st.text_input("Observações")

    if st.button("Enviar Pedido"):
        if nome and sabor:
            pedido = {
                "nome": nome,
                "sabor": sabor,
                "obs": obs,
                "criado_em": datetime.utcnow().timestamp()
            }
            db.reference('pedidos').push(pedido)
            st.success("Pedido enviado!")
        else:
            st.warning("Preencha nome e sabor")

# =========================
# MODO COZINHA
# =========================
if modo == "Cozinha":

    st.subheader("🔥 Fila de Produção")

    ref = db.reference('pedidos')
    dados = ref.get()

    if dados:
        pedidos_lista = list(dados.items())

        # ordenar por criação (mais correto que key)
        pedidos_lista = sorted(
            pedidos_lista,
            key=lambda x: x[1].get("criado_em", 0)
        )

        agora = datetime.utcnow()

        for i, (key, pedido) in enumerate(pedidos_lista):

            tempo_preparo = 15 + (i * 10)

            # inicializa tempo
            if "inicio" not in pedido:
                inicio_ts = datetime.utcnow().timestamp()
                db.reference(f'pedidos/{key}/inicio').set(inicio_ts)
                inicio = datetime.fromtimestamp(inicio_ts)
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

            # FINALIZAR
            if st.button(f"Finalizar Pedido {i+1}", key=key):
                db.reference(f'pedidos/{key}').delete()
                st.rerun()

            st.divider()

    else:
        st.info("Sem pedidos")

# =========================
# LISTA GERAL (OPCIONAL)
# =========================
st.divider()
st.subheader("📋 Visão Geral")

ref = db.reference('pedidos')
dados = ref.get()

if dados:
    pedidos_lista = list(dados.values())
    pedidos_lista.reverse()

    for i, pedido in enumerate(pedidos_lista):
        st.markdown(f"""
        **Pedido {i+1}**  
        👤 {pedido.get('nome', '')}  
        🍕 {pedido.get('sabor', '')}  
        📝 {pedido.get('obs', '')}
        """)
else:
    st.info("Nenhum pedido ainda")
