import matplotlib.pyplot as plt

def plot_resultados(resultados):
    fig, ax = plt.subplots(figsize=(6, 2))
    cumulativo = [sum(resultados[:i+1]) for i in range(len(resultados))]
    ax.plot(cumulativo, marker='o')
    ax.set_title("Lucro/Prejuízo Acumulado")
    ax.grid(True)
    return fig
