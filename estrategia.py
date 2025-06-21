def analisar_ticks_famped(ticks):
    menores_que_4 = [d for d in ticks if d < 4]
    if len(menores_que_4) >= 6:
        return {"entrada": "DIGITOVER 4", "estrategia": "Famped"}
    return {"entrada": "ESPERAR", "estrategia": "Famped"}
