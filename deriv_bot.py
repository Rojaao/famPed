
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
        stake_inicial = self.stake
        stake = stake_inicial
        martingale_nivel = 0

        def receber_ticks():
            nonlocal ticks, ws
            while True:
                try:
                    tick_msg = json.loads(ws.recv())
                    if tick_msg.get("msg_type") == "tick":
                        ticks.append(int(str(tick_msg["tick"]["quote"])[-1]))
                        if len(ticks) > 100:
                            ticks = ticks[-100:]
                except Exception as e:
                    self.logs.append(f"❌ Erro no recebimento de ticks: {str(e)}")
                    stframe.text("\n".join(self.logs[-12:]))
                    time.sleep(2)

        threading.Thread(target=receber_ticks, daemon=True).start()

        while True:
            if len(ticks) >= 33:
                analise = analisar_ticks_famped(ticks[-33:])
                entrada = analise['entrada']
                estrategia = analise['estrategia']

                if entrada == "ESPERAR":
                    self.logs.append("⏸ Aguardando oportunidade...")
                    stframe.text("\n".join(self.logs[-12:]))
                    time.sleep(2)
                    continue

                barrier = entrada.split()[-1]

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
                        "barrier": barrier
                    },
                    "req_id": 1
                }

                ws.send(json.dumps(contrato))
                result = json.loads(ws.recv())

                if result.get("msg_type") != "buy" or "buy" not in result:
                    self.logs.append("❌ Erro: resposta inesperada da Deriv (sem campo 'buy')")
                    stframe.text("\n".join(self.logs[-12:]))
                    time.sleep(3)
                    continue

                buy_id = result["buy"]["contract_id"]
                resultado = "Desconhecido"
                inicio = time.time()

                while True:
                    try:
                        res = json.loads(ws.recv())
                        if res.get("msg_type") == "proposal_open_contract":
                            if res["proposal_open_contract"]["contract_id"] == buy_id:
                                if res["proposal_open_contract"]["is_sold"]:
                                    lucro = res["proposal_open_contract"]["profit"]
                                    resultado = "WIN" if lucro > 0 else "LOSS"
                                    break
                        if time.time() - inicio > 10:
                            self.logs.append("⚠️ Timeout ao aguardar resultado.")
                            break
                    except:
                        break

                if resultado == "WIN":
                    ganho_total += stake
                    consecutivas = 0
                    stake = stake_inicial
                    martingale_nivel = 0
                    self.logs.append(f"✅ WIN | Lucro: +${round(lucro, 2)} | Stake: {round(stake, 2)}")
                else:
                    ganho_total -= stake
                    consecutivas += 1
                    if self.use_martingale:
                        martingale_nivel += 1
                        stake = round(stake_inicial * (self.factor ** martingale_nivel), 2)
                        self.logs.append(f"❌ LOSS | Prejuízo: -${round(stake, 2)} | Martingale nível {martingale_nivel} | Próxima stake: {stake}")
                    else:
                        self.logs.append(f"❌ LOSS | Prejuízo: -${round(stake, 2)}")

                log = f"[{time.strftime('%H:%M:%S')}] Estratégia: {estrategia} | Entrada: {entrada} | Resultado: {resultado}"
                self.logs.append(log)
                self.resultados.append(1 if resultado == "WIN" else -1)

                stframe.text("\n".join(self.logs[-12:]))
                plot_area.pyplot(plot_resultados(self.resultados))

                if ganho_total >= self.stop_gain:
                    self.logs.append("🎯 Meta de lucro atingida. Parando o robô.")
                    break
                if ganho_total <= -self.stop_loss or consecutivas >= self.max_losses:
                    self.logs.append("🛑 Stop Loss ou limite de perdas consecutivas atingido.")
                    break

                # Reset de análise após cada operação
                ticks = []

                time.sleep(5)
