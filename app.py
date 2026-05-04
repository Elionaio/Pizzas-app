import streamlit as st
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# =========================
# AUTO REFRESH
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

st.title("🍕 Sistema de Pedidos")

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

    # =========================
    # 🎤 VOZ FUNCIONAL
    # =========================
    st.subheader("🎤 Ditado por voz")

    voz = st.text_input("Texto da voz")

    components.html("""
    <button onclick="startRecognition()" style="font-size:18px;padding:10px;">
        🎤 Falar
    </button>

    <p id="status">Clique e fale</p>

    <script>
    function startRecognition() {

        const recognition = new webkitSpeechRecognition();

        recognition.lang = "pt-BR";
        recognition.continuous = false;
        recognition.interimResults = false;

        document.getElementById("status").innerHTML = "Ouvindo...";

        recognition.start();

        recognition.onresult = function(event) {
            const text = event.results[0][0].transcript;

            document.getElementById("status").innerHTML = "Você disse: " + text;

            // ⚠️ mais seguro: pega o último input (voz)
            const inputs = window.parent.document.querySelectorAll('input');
            const voiceInput = inputs[inputs.length - 1];

            if (voiceInput) {
                voiceInput.value = text;
                voiceInput.dispatchEvent(new Event("input", { bubbles: true }));
            }
        };

        recognition.onerror = function(event) {
            document.getElementById("status").innerHTML = "Erro: " + event.error;
        };
    }
    </script>
    """, height=120)

    # =========================
    # PROCESSAMENTO VOZ
    # =========================
    if voz:
        st.success(f"🎤 Você disse: {voz}")

        c = voz.lower()

        if "calabresa" in c:
            sabor = "Calabresa"
        elif "frango" in c:
            sabor = "Frango"

        if "sem cebola" in c:
            obs = "Sem cebola"

    # =========================
    # ENVIAR PEDIDO
    # =========================
    if st.button("Enviar Pedido"):

        if nome and sabor:

            pedido = {
                "nome": nome,
                "sabor": sabor,
                "obs": obs,
                "criado_em": datetime.utcnow().timestamp(),
                "inicio": None,
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

    if dados:

        pedidos_lista = list(dados.items())
        pedidos_lista.sort(key=lambda x: x[1].get("criado_em", 0))

        agora = datetime.utcnow().timestamp()

        col1, col2 = st.columns(2)
        pedidos_ativos = pedidos_lista[:2]

        for i, (key, pedido) in enumerate(pedidos_ativos):

            tempo_preparo = 15 + (i * 10)

            inicio = pedido.get("inicio")

            # =========================
            # INICIAR SÓ UMA VEZ
            # =========================
            if inicio is None:
                inicio = agora
                db.reference(f'pedidos/{key}').update({
                    "inicio": inicio,
                    "status": "em_preparo"
                })

            fim = inicio + (tempo_preparo * 60)
            restante = fim - agora

            minutos = int(restante // 60)
            segundos = int(restante % 60)

            # =========================
            # STATUS
            # =========================
            if restante <= 0:
                status = "✅ PRONTO"
                cor = "#16a34a"
            elif restante < 300:
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
                font-family:Arial;
            ">
                <h2>{pedido.get('sabor','')}</h2>
                <h3>{pedido.get('nome','')}</h3>
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
            ⏱ {pedido.get('status','')}
            """)

            st.divider()

    else:
        st.info("Nenhum pedido ainda")
