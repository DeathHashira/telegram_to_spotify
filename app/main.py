from gui.gui import *
from db.schema import run
import sys, os

if not os.path.exists('spotify.db'):
    run()

def load_stylesheet(file_path):
    with open(file_path, "r") as f:
        return f.read()

app = QApplication(sys.argv)
app.setStyleSheet(load_stylesheet("theme.qss"))
MyMainWindow = MainWindow()

MyMainWindow.show()
sys.exit(app.exec())