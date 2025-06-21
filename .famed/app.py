import streamlit as st
import sys
import os

# Garante que os outros arquivos sejam encontrados
sys.path.append(os.path.dirname(__file__))

from deriv_bot import DerivBot

# Configuração da página
st.set_page_config(page_title="FamPed - Robô Inteligente da Deriv (by Rogger Pedro)", layout="wide")
st.title("🤖 FamPed - Robô Inteligente da Deriv (by Rogger Pedro)")

# Campos de entrada
token = st.text_input("🔑 Token da Deriv", type="password")
symbol = st.selectbox("📈 Ativo", options=["R_100", "R_10"])
stake = st.number_input("💵 Stake inicial", min_value=0.01, value=0.35, step=0.01)
use_martingale = st.checkbox("🎯 Usar Martingale", value=True)
factor = st.number_input("📈 Fator Martingale", min_value=1.0, value=2.0, step=0.1)
stop_gain = st.number_input("💰 Meta de lucro (Stop Gain)", value=10.0)
stop_loss = st.number_input("📉 Limite de perda (Stop Loss)", value=10.0)
max_losses = st.number_input("❌ Máximo de perdas consecutivas", value=3, step=1)

# Botão de iniciar
start_button = st.button("🚀 Iniciar Robô")

# Ao clicar em iniciar
if start_button and token:
    st.success("Robô iniciado com sucesso!")
    bot = DerivBot(
        token=token,
        symbol=symbol,
        stake=stake,
        use_martingale=use_martingale,
        factor=factor,
        stop_gain=stop_gain,
        stop_loss=stop_loss,
        max_losses=max_losses
    )
    bot.run_interface()
