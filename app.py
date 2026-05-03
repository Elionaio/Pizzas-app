import streamlit as st
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# =========================
# AUTO REFRESH
# =========================
st_autorefresh(interval=2000, key="refresh")

# =========================
# FIREBASE
# =========================
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://pizza-app-e6fb5-default-rtdb.firebaseio.com'
    })

# =========================
# TÍTULO
# =========================
st.title("🍕 Sistema de Pedidos")

modo = st.radio("Modo", ["📝 Atendente", "🔥 Produção", "📋 Lista"])

ref = db.reference('pedidos')
dados = ref.get()

# =========================
# 📝 ATENDENTE
# =========================
if modo == "📝 Atendente":

    st.subheader("Novo Pedido")

    nome = st.text_input("Nome")
    sabor = st.text_input("Sabor")
    obs = st.text_input("Observações")

    # 🎤 VOZ
    st.subheader("🎤 Falar")

    comando = components.html("""
        <button onclick="startRecognition()" style="font-size:20px;padding:10px;">
        🎤 Falar
        </button>

        <p id="output"></p>

        <script>
        function startRecognition() {
            var recognition = new webkitSpeechRecognition();
            recognition.lang = "pt-BR";
            recognition.start();

            recognition.onresult = function(event) {
                var text = event.results[0][0].transcript;

                window.parent.postMessage({
                    type: "streamlit:setComponentValue",
                    value: text
                }, "*");
            }
        }
        </script>
    """, height=100)

    if comando:
        st.success(f"Você disse: {comando}")

        c = comando.lower()

        if "calabresa" in c:
            sabor = "Calabresa"

        if "frango" in c:
            sabor = "Frango"

        if "sem cebola" in c:
            obs = "Sem cebola"

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
# 🔥 PRODUÇÃO
# =========================
elif modo == "🔥 Produção":

    if dados:
        pedidos_lista = list(dados.items())

        pedidos_lista = sorted(
            pedidos_lista,
            key=lambda x: x[1].get("criado_em", 0)
        )

        agora = datetime.utcnow()

        col1, col2 = st.columns(2)
        pedidos_ativos = pedidos_lista[:2]

        for i, (key, pedido) in enumerate(pedidos_ativos):

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
                cor = "#16a34a"
            elif restante.total_seconds() < 300:
                status = "⚠️ QUASE"
                cor = "#f59e0b"
            else:
                status = "🔥 EM PREPARO"
                cor = "#dc2626"

            bloco = f"""
            <div style="
                height:300px;
                display:flex;
                flex-direction:column;
                justify-content:center;
                align-items:center;
                border-radius:15px;
                background:{cor};
                color:white;
                text-align:center;
            ">
                <h2>{pedido.get('sabor','')}</h2>
                <h3>{pedido.get('nome','')}</h3>
                <h1>{minutos}m {segundos}s</h1>
                <p>{status}</p>
            </div>
            """

            if i == 0:
                with col1:
                    st.markdown(bloco, unsafe_allow_html=True)
                    if st.button("Finalizar", key=key):
                        db.reference(f'pedidos/{key}').delete()
                        st.rerun()
            else:
                with col2:
                    st.markdown(bloco, unsafe_allow_html=True)
                    if st.button("Finalizar", key=key):
                        db.reference(f'pedidos/{key}').delete()
                        st.rerun()
    else:
        st.info("Sem pedidos")

# =========================
# 📋 LISTA
# =========================
else:

    st.subheader("Lista de Pedidos")

    if dados:
        pedidos_lista = list(dados.values())
        pedidos_lista.reverse()

        for i, pedido in enumerate(pedidos_lista):
            st.markdown(f"""
            **Pedido {i+1}**  
            👤 {pedido.get('nome','')}  
            🍕 {pedido.get('sabor','')}  
            📝 {pedido.get('obs','')}
            """)
            st.divider()
    else:
        st.info("Nenhum pedido ainda")
