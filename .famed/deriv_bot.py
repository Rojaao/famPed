import websocket, json, time, threading
import streamlit as st
from estrategia import analisar_ticks_famped
from utils import plot_resultados

class DerivBot:
    def __init__(self, token, symbol, stake, use_martingale, factor, stop_gain, stop_loss, max_losses):
        self.token = token
        self.symbol = symbol
        self.stake = stake
        self.use_martingale = use_martingale
        self.factor = factor
        self.stop_gain = stop_gain
        self.stop_loss = stop_loss
        self.max_losses = max_losses

        self.logs = []
        self.resultados = []

    def run_interface(self):
        stframe = st.empty()
        plot_area = st.empty()

        ws = websocket.WebSocket()
        ws.connect("wss://ws.binaryws.com/websockets/v3?app_id=1089")
        ws.send(json.dumps({"authorize": self.token}))
        auth_response = json.loads(ws.recv())
        if 'error' in auth_response:
            st.error("❌ Token inválido")
            return

        st.success(f"✅ Conectado | Conta: {'Real' if auth_response['authorize']['is_virtual']==0 else 'Demo'}")

        ws.send(json.dumps({"ticks": self.symbol}))
        ticks = []

        saldo = 0
        consecutivas = 0
        ganho_total = 0
        stake = self.stake

        def receber_ticks():
            nonlocal ticks
            while True:
                tick_msg = json.loads(ws.recv())
                if tick_msg.get("msg_type") == "tick":
                    ticks.append(int(str(tick_msg["tick"]["quote"])[-1]))
                    if len(ticks) > 100:
                        ticks = ticks[-100:]

        threading.Thread(target=receber_ticks, daemon=True).start()

        while True:
            if len(ticks) >= 33:
                analise = analisar_ticks_famped(ticks[-33:])
                entrada = analise['entrada']
                estrategia = analise['estrategia']

                contrato = {
                    "buy": 1,
                    "price": round(stake, 2),
                    "parameters": {
                        "amount": round(stake, 2),
                        "basis": "stake",
                        "contract_type": "DIGITOVER",
                        "currency": "USD",
                        "duration": 1,
                        "duration_unit": "t",
                        "symbol": self.symbol,
                        "barrier": entrada[-1]
                    },
                    "req_id": 1
                }
                ws.send(json.dumps(contrato))
                result = json.loads(ws.recv())
                if "error" in result:
                    self.logs.append(f"Erro: {result['error']['message']}")
                    break
                buy_id = result["buy"]["contract_id"]
                start_time = time.time()

                resultado = "Desconhecido"
                while True:
                    res = json.loads(ws.recv())
                    if res.get("msg_type") == "proposal_open_contract" and res["proposal_open_contract"]["contract_id"] == buy_id:
                        if res["proposal_open_contract"]["is_sold"]:
                            resultado = "WIN" if res["proposal_open_contract"]["profit"] > 0 else "LOSS"
                            break
                    if time.time() - start_time > 10:
                        break

                if resultado == "WIN":
                    ganho_total += stake
                    consecutivas = 0
                    stake = self.stake
                else:
                    ganho_total -= stake
                    consecutivas += 1
                    if self.use_martingale:
                        stake *= self.factor

                log = f"[{time.strftime('%H:%M:%S')}] Estratégia: {estrategia} | Entrada: {entrada} | Resultado: {resultado} | Stake: {round(stake,2)}"
                self.logs.append(log)
                self.resultados.append(1 if resultado == "WIN" else -1)

                stframe.text("
".join(self.logs[-12:]))
                plot_area.pyplot(plot_resultados(self.resultados))

                if ganho_total >= self.stop_gain:
                    self.logs.append("🎯 Meta de lucro atingida. Parando o robô.")
                    break
                if ganho_total <= -self.stop_loss or consecutivas >= self.max_losses:
                    self.logs.append("🛑 Stop Loss ou limite de perdas consecutivas atingido.")
                    break

                time.sleep(5)
