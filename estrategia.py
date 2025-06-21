def analisar_ticks_famped(ticks):
    ultimos_8 = ticks[-8:]
    ausencia_baixos = all(d >= 4 for d in ultimos_8)
    media = sum(ticks) / len(ticks)

    if ausencia_baixos:
        entrada = "OVER 3"
    elif media > 5.5:
        entrada = "OVER 4"
    else:
        entrada = "OVER 3"

    return {"estrategia": "FAMPED", "entrada": entrada}