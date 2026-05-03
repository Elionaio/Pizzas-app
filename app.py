import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, timedelta

# =========================
# AUTO REFRESH
# =========================
st.autorefresh(interval=2000, key="refresh")

# =========================
# CONEXÃO FIREBASE
# =========================
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://pizza-app-e6fb5-default-rtdb.firebaseio.com'
    })

# =========================
# INTERFACE
# =========================
st.title("🍕 Sistema de Pedidos")

# Botão para alternar entre lista e tela cheia
modo_producao = st.checkbox("Modo Produção (Tela Cheia)")

if modo_producao:
    # =========================
    # MODO PRODUÇÃO (DUAS COLUNAS)
    # =========================
    st.subheader("🔥 Fila de Produção")

    col1, col2 = st.columns(2)  # duas colunas lado a lado

    ref = db.reference('pedidos')
    dados = ref.get()

    if dados:
        pedidos_lista = list(dados.items())
        pedidos_lista = sorted(pedidos_lista, key=lambda x: x[0])  # ordenar por chave de chegada

        agora = datetime.utcnow()

        for i, (key, pedido) in enumerate(pedidos_lista):
            tempo_preparo = 15 + (i * 10)

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
                status = "✅ PRONTO"
                cor = "green"
                st.audio("https://www.soundjay.com/buttons/beep-01a.mp3")
            elif restante.total_seconds() < 300:
                status = f"⚠️ {minutos}m {segundos}s"
                cor = "orange"
            else:
                status = f"⏳ {minutos}m {segundos}s"
                cor = "red"

            col_index = i % 2  # alterna entre colunas

            if col_index == 0:
                with col1:
                    st.markdown(f"""
                    <div style="padding:15px;border-radius:10px;background-color:{cor};color:white">
                    <h3>🍕 Pedido {i+1}</h3>
                    👤 {pedido.get('nome', '')}<br>
                    🍕 {pedido.get('sabor', '')}<br>
                    📝 {pedido.get('obs', '')}<br><br>
                    ⏱️ Tempo: {tempo_preparo} min<br>
                    🔥 Status: {status}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                with col2:
                    st.markdown(f"""
                    <div style="padding:15px;border-radius:10px;background-color:{cor};color:white">
                    <h3>🍕 Pedido {i+1}</h3>
                    👤 {pedido.get('nome', '')}<br>
                    🍕 {pedido.get('sabor', '')}<br>
                    📝 {pedido.get('obs', '')}<br><br>
                    ⏱️ Tempo: {tempo_preparo} min<br>
                    🔥 Status: {status}
                    </div>
                    """, unsafe_allow_html=True)

            # BOTÃO FINALIZAR
            if st.button(f"Finalizar Pedido {i+1}", key=key):
                db.reference(f'pedidos/{key}').delete()
                st.rerun()

            st.divider()

    else:
        st.info("Sem pedidos")

else:
    # =========================
    # MODO LISTA SIMPLES
    # =========================
    st.subheader("📋 Pedidos em Lista")

    ref = db.reference('pedidos')
    dados = ref.get()

    if dados:
        pedidos_lista = list(dados.values())
        pedidos_lista.reverse()

        for i, pedido in enumerate(pedidos_lista):
            st.markdown(f"""
            **Pedido {i+1}**  
            👤 **Cliente:** {pedido.get('nome', '')}  
            🍕 **Sabor:** {pedido.get('sabor', '')}  
            📝 **Obs:** {pedido.get('obs', '')}
            """)
            st.divider()
    else:
