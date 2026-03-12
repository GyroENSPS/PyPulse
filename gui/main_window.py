# Fenêtre principale (à implémenter)
from PyQt5.QtWidgets import QMainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyPulse")
        self.resize(1200, 800)
        # TODO : ajouter les widgets
