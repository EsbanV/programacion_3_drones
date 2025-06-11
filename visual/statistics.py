import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class GeneralStatisticsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.label = ttk.Label(self, text="Estadísticas Generales", font=("Helvetica", 16))
        self.label.pack(pady=10)

        self.fig, self.axs = plt.subplots(1, 2, figsize=(10, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack()

        self.update_graphs()

    def update_graphs(self):
        nodos_mas_visitados = {
            "Cliente": 12,
            "Almacenamiento": 7,
            "Abastecimiento": 9
        }

        nodos_por_rol = {
            "Cliente": 50,
            "Almacenamiento": 20,
            "Abastecimiento": 30
        }

        for ax in self.axs:
            ax.clear()

        self.axs[0].bar(nodos_mas_visitados.keys(), nodos_mas_visitados.values(), color=["skyblue", "lightgreen", "salmon"])
        self.axs[0].set_title("Nodos más visitados")
        self.axs[0].set_ylabel("Cantidad de visitas")

        self.axs[1].pie(nodos_por_rol.values(), labels=nodos_por_rol.keys(), autopct="%1.1f%%", startangle=90)
        self.axs[1].set_title("Proporción de nodos por rol")

        self.fig.tight_layout()
        self.canvas.draw()
#----------------------------------------------------Pestaña 5----------------------------------------------------#
#Falta implementar el resto del codigo donde obtendra los valores para los graficos y los mostrara en la pestaña
#cuando este listo el codigo la completo pero eso deberia de funcionar
