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

    # =========================
    # 🎤 VOZ (DITADO + COPIAR)
    # =========================
    st.subheader("🎤 Ditado por voz")

    components.html("""
        <button onclick="startRecognition()" style="font-size:18px;padding:10px;">
        🎤 Falar
        </button>

        <input id="campo" style="width:100%;font-size:18px;margin-top:10px;" placeholder="O texto aparece aqui..." />

        <button onclick="copiar()" style="margin-top:10px;padding:8px;">
        📋 Copiar texto
        </button>

        <script>
        var recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition();

            recognition.lang = "pt-BR";
            recognition.interimResults = true;
            recognition.continuous = true;

            recognition.start();

            recognition.onresult = function(event) {
                let texto = "";

                for (let i = event.resultIndex; i < event.results.length; i++) {
                    texto += event.results[i][0].transcript;
                }

                document.getElementById("campo").value = texto;
            };
        }

        function copiar() {
            var campo = document.getElementById("campo");
            campo.select();
            document.execCommand("copy");
            alert("Texto copiado!");
        }
        </script>
    """, height=180)

    voz_texto = st.text_input("Colar texto da voz aqui (copiado)")

    if voz_texto:
        c = voz_texto.lower()

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
