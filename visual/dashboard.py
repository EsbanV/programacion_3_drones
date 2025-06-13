import tkinter as tk
from tkinter import ttk
from visual.statistics import GeneralStatisticsTab

class Dashboard(ttk.Notebook):
    def __init__(self, parent):
        super().__init__(parent)

        self.stats_tab = GeneralStatisticsTab(self)
        self.add(self.stats_tab, text="Estadísticas")
