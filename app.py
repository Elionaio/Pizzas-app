import streamlit as st
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# =========================
# AUTO REFRESH (1s)
# =========================
st_autorefresh(interval=1000, key="refresh")

# =========================
# FIREBASE
# =========================
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://pizza-app-e6fb5-default-rtdb.firebaseio.com'
    })

st.title("🍕 Sistema de Pedidos PRO")

modo = st.radio("Modo", ["📝 Atendente", "🔥 Produção", "📋 Lista"])

ref = db.reference('pedidos')
dados = ref.get() or {}

# =========================
# 📝 ATENDENTE
# =========================
if modo == "📝 Atendente":

    st.subheader("Novo Pedido")

    nome = st.text_input("Nome")
    sabor = st.text_input("Sabor")
    obs = st.text_input("Observações")

    if st.button("Enviar Pedido"):

        if nome and sabor:

            # 🔥 posição atual da fila = tamanho atual
            posicao_fila = len(dados)

            # 🔥 tempo base + atraso por fila (fixo no pedido)
            tempo_base = 15
            tempo_total = tempo_base + (posicao_fila * 10)

            pedido = {
                "nome": nome,
                "sabor": sabor,
                "obs": obs,
                "criado_em": datetime.utcnow().timestamp(),
                "inicio": None,
                "tempo_total": tempo_total * 60,  # segundos
                "status": "novo"
            }

            ref.push(pedido)

            st.success("Pedido enviado!")

        else:
            st.warning("Preencha nome e sabor")

# =========================
# 🔥 PRODUÇÃO
# =========================
elif modo == "🔥 Produção":

    pedidos = list(dados.items())

    # ordem real de chegada
    pedidos.sort(key=lambda x: x[1].get("criado_em", 0))

    agora = datetime.utcnow().timestamp()

    col1, col2 = st.columns(2)

    ativos = pedidos[:2]

    for i, (key, p) in enumerate(ativos):

        # =========================
        # INÍCIO FIXO (NÃO MUDA MAIS)
        # =========================
        inicio = p.get("inicio")

        if inicio is None:
            inicio = agora
            db.reference(f'pedidos/{key}').update({
                "inicio": inicio,
                "status": "em_preparo"
            })

        # =========================
        # TIMER REAL
        # =========================
        fim = inicio + p.get("tempo_total", 900)
        restante = fim - agora

        minutos = int(restante // 60)
        segundos = int(restante % 60)

        # =========================
        # STATUS VISUAL
        # =========================
        if restante <= 0:
            status = "✅ PRONTO"
            cor = "#16a34a"
        elif restante < 300:
            status = "⚠️ QUASE PRONTO"
            cor = "#f59e0b"
        else:
            status = "🔥 EM PREPARO"
            cor = "#dc2626"

        bloco = f"""
        <div style="
            height:280px;
            display:flex;
            flex-direction:column;
            justify-content:center;
            align-items:center;
            border-radius:16px;
            background:{cor};
            color:white;
            font-family:Arial;
            box-shadow:0 6px 18px rgba(0,0,0,0.2);
        ">
            <h2>{p.get('sabor','')}</h2>
            <h3>{p.get('nome','')}</h3>
            <h1>{minutos}m {segundos}s</h1>
            <p>{status}</p>
        </div>
        """

        col = col1 if i == 0 else col2

        with col:
            st.markdown(bloco, unsafe_allow_html=True)

            if st.button("Finalizar", key=key):
                db.reference(f'pedidos/{key}').delete()
                st.rerun()

    if not ativos:
        st.info("Nenhum pedido em produção")

# =========================
# 📋 LISTA (MELHORADA)
# =========================
else:

    if not dados:
        st.info("Nenhum pedido ainda")
    else:

        st.subheader("📋 Todos os pedidos")

        pedidos = list(dados.items())
        pedidos.sort(key=lambda x: x[1].get("criado_em", 0), reverse=True)

        for key, p in pedidos:

            status = p.get("status", "novo")

            cor = {
                "novo": "#3b82f6",
                "em_preparo": "#f59e0b",
                "pronto": "#16a34a"
            }.get(status, "#999")

            st.markdown(f"""
            <div style="
                padding:10px;
                border-left:6px solid {cor};
                margin-bottom:10px;
                background:#1111;
                border-radius:8px;
            ">
                👤 <b>{p.get('nome','')}</b><br>
                🍕 {p.get('sabor','')}<br>
                📝 {p.get('obs','')}<br>
                ⏱ {status}
            </div>
            """, unsafe_allow_html=True)
