# Point d'entrée principal de PyPulse
import sys
from PyQt5.QtWidgets import QApplication
# from gui.main_window import MainWindow  # à décommenter quand la GUI sera prête

def main():
    app = QApplication(sys.argv)
    # window = MainWindow()
    # window.show()
    print("PyPulse démarré.")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
