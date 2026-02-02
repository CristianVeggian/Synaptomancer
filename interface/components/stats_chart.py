from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt6.QtWidgets import QSizePolicy


class StatsChart(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(4, 4))
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def clear(self):
        self.ax.clear()
        self.draw()

    def plot_bar(self, labels, values, title="", ylabel=""):
        self.ax.clear()
        self.ax.bar(labels, values)
        self.ax.set_title(title)
        self.ax.set_ylabel(ylabel)
        self.draw()

    def plot_pie(self, labels, values, title=""):
        self.ax.clear()
        self.ax.pie(values, labels=labels, autopct="%1.1f%%")
        self.ax.set_title(title)
        self.draw()
