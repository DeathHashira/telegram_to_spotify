from gui.gui import *
import sys

def load_stylesheet(file_path):
    with open(file_path, "r") as f:
        return f.read()

app = QApplication(sys.argv)
app.setStyleSheet(load_stylesheet("theme.qss"))
MyMainWindow = MainWindow()

MyMainWindow.show()
sys.exit(app.exec())