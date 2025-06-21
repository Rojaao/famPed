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
        stake_inicial = self.stake  # salva stake original

        def receber_ticks():
            nonlocal ticks, ws
            while True:
                try:
                    tick_msg = json.loads(ws.recv())
                    if tick_msg.get("msg_type") == "tick":
                        ticks.append(int(str(tick_msg["tick"]["quote"])[-1]))
                        if len(ticks) > 100:
                            ticks = ticks[-100:]
                except websocket.WebSocketConnectionClosedException:
                    self.logs.append("⚠️ Conexão perdida. Reconectando ao WebSocket...")
                    stframe.text("\n".join(self.logs[-12:]))
                    try:
                        ws = websocket.WebSocket()
                        ws.connect("wss://ws.binaryws.com/websockets/v3?app_id=1089")
                        ws.send(json.dumps({"authorize": self.token}))
                        ws.recv()
                        ws.send(json.dumps({"ticks": self.symbol}))
                        self.logs.append("✅ Reconectado com sucesso.")
                        stframe.text("\n".join(self.logs[-12:]))
                    except Exception as e:
                        self.logs.append(f"❌ Erro ao reconectar: {str(e)}")
                        stframe.text("\n".join(self.logs[-12:]))
                        time.sleep(5)
                except Exception as e:
                    self.logs.append(f"❌ Erro inesperado: {str(e)}")
                    stframe.text("\n".join(self.logs[-12:]))
                    time.sleep(2)

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
                    self.logs.append(f"❌ Erro ao comprar contrato: {result['error']['message']}")
                    stframe.text("\n".join(self.logs[-12:]))
                    time.sleep(3)
                    continue

                if "buy" not in result:
                    self.logs.append("❌ Erro: resposta inesperada da Deriv (sem campo 'buy')")
                    stframe.text("\n".join(self.logs[-12:]))
                    time.sleep(3)
                    continue

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
                    stake = stake_inicial  # ✅ volta ao valor original após win
                else:
                    ganho_total -= stake
                    consecutivas += 1
                    if self.use_martingale:
                        stake *= self.factor  # aplica martingale
