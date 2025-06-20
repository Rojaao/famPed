import streamlit as st
from deriv_bot import DerivBot

st.set_page_config(page_title="FamPed | Robô Inteligente da Deriv")

st.title("🤖 FamPed | Robô Automático da Deriv")
st.markdown("Robô com estratégia automática inteligente para operar com segurança.")

# Inputs do usuário
token = st.text_input("🔑 Token da Deriv", type="password")
stake = st.number_input("💵 Stake inicial", min_value=0.01, value=0.35, step=0.01)
use_martingale = st.checkbox("🎯 Usar Martingale", value=True)
factor = st.number_input("📈 Fator Martingale", min_value=1.0, value=2.0, step=0.1)
stop_gain = st.number_input("💰 Meta de lucro (Stop Gain)", value=10.0)
stop_loss = st.number_input("📉 Limite de perda (Stop Loss)", value=10.0)
max_losses = st.number_input("❌ Máximo de perdas consecutivas", value=3, step=1)
start_button = st.button("🚀 Iniciar Robô")

if start_button and token:
    st.success("Robô iniciado com sucesso!")
    # Simulação de chamada ao bot (a lógica completa está em deriv_bot.py)
    bot = DerivBot(token, stake, use_martingale, factor, stop_gain, stop_loss, max_losses)
    bot.run()