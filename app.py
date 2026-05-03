# Pizzas-app
import streamlit as st
import time

# Estado
if "pedidos" not in st.session_state:
    st.session_state.pedidos = []

if "atual" not in st.session_state:
    st.session_state.atual = None

st.title("🍕 Pedidos da Pizzaria")

# ===== NOVO PEDIDO =====
st.header("Novo Pedido")

nome = st.text_input("Nome do Cliente")
pizza = st.text_input("Sabor")
obs = st.text_input("Observação")

if st.button("Enviar Pedido"):
    if nome and pizza:
        st.session_state.pedidos.append({
            "nome": nome,
            "pizza": pizza,
            "obs": obs
        })
        st.success("Pedido enviado!")

# ===== PRODUÇÃO =====
st.header("Produção")

if st.session_state.atual is None and st.session_state.pedidos:
    st.session_state.atual = st.session_state.pedidos.pop(0)
    st.session_state.inicio = time.time()

if st.session_state.atual:
    p = st.session_state.atual

    st.subheader("Pedido Atual")
    st.write(f"Cliente: {p['nome']}")
    st.write(f"Pizza: {p['pizza']}")
    st.write(f"Obs: {p['obs']}")

    tempo_passado = int(time.time() - st.session_state.inicio)
    tempo_total = 15 * 60
    restante = max(0, tempo_total - tempo_passado)

    st.write(f"⏱ {restante//60}:{restante%60:02d}")

    if st.button("Próximo Pedido"):
        st.session_state.atual = None
        st.rerun()

# ===== FILA =====
st.header("Fila")

for i, p in enumerate(st.session_state.pedidos):
    tempo = 15 + (i * 10)
    st.write(f"{i+1}. {p['nome']} - {p['pizza']} (⏱ {tempo} min)")
