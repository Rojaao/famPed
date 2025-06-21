
import streamlit as st
from deriv_bot import DerivBot

st.title("🤖 Robô Deriv - Estratégia FAMPED")
token = st.text_input("Token da Deriv", type="password")
symbol = st.selectbox("Ativo", ["R_100", "R_10", "R_50"])
stake = st.number_input("Stake inicial", value=0.35, step=0.01)
use_martingale = st.checkbox("Usar Martingale?", value=True)
factor = st.number_input("Fator Martingale", value=2.0, step=0.1)
stop_gain = st.number_input("Stop Gain (lucro alvo)", value=5.0, step=0.5)
stop_loss = st.number_input("Stop Loss (perda máxima)", value=5.0, step=0.5)
max_losses = st.number_input("Máx. perdas consecutivas", value=3, step=1)

if st.button("🚀 Iniciar Robô"):
    bot = DerivBot(token, symbol, stake, use_martingale, factor, stop_gain, stop_loss, int(max_losses))
    bot.run_interface()
