import sys
from PyQt6.QtWidgets import QApplication, QMainWindow

from app.ui.main_widget_ui import Ui_MainWindow


class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Patopo - Toolbox")
        self.ui.label_version.setText("v0.0.0")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainUI()
    main.show()
    sys.exit(app.exec())

# pyinstaller --clean --noconsole --onefile -n PTPtoolbox -p . --collect-submodules app app/main.py
