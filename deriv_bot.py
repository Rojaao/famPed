import time
from estrategia import analisar_ticks_famped

class DerivBot:
    def __init__(self, token, stake, use_martingale, factor, stop_gain, stop_loss, max_losses):
        self.token = token
        self.stake = stake
        self.use_martingale = use_martingale
        self.factor = factor
        self.stop_gain = stop_gain
        self.stop_loss = stop_loss
        self.max_losses = max_losses

    def run(self):
        logs = []
        saldo = 100.0
        consecutivas = 0
        ganho_total = 0
        stake = self.stake

        ticks = [7, 8, 5, 6, 9, 7, 6, 8, 3, 1, 2, 4, 6, 7, 3, 2, 1, 0, 4, 5, 6, 7, 2, 3, 4, 5, 6, 7, 8, 9, 3, 1, 0]

        for i in range(10):
            analise = analisar_ticks_famped(ticks)
            entrada = analise['entrada']
            estrategia = analise['estrategia']
            resultado = "WIN" if i % 2 == 0 else "LOSS"

            if resultado == "WIN":
                ganho_total += stake
                consecutivas = 0
                stake = self.stake
            else:
                ganho_total -= stake
                consecutivas += 1
                if self.use_martingale:
                    stake *= self.factor

            logs.append(f"[{time.strftime('%H:%M:%S')}] Estratégia: {estrategia} | Entrada: {entrada} | Resultado: {resultado} | Stake: {round(stake,2)}")

            if ganho_total >= self.stop_gain:
                logs.append("🎯 Meta de lucro atingida. Parando o robô.")
                break
            if ganho_total <= -self.stop_loss or consecutivas >= self.max_losses:
                logs.append("🛑 Limite de perda ou de perdas consecutivas atingido. Parando o robô.")
                break

            time.sleep(1)
        return logs