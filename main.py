import sys
from PyQt5.QtWidgets import QApplication
import view

app = QApplication(sys.argv)
win = view.view_window()
win.show()
sys.exit(app.exec())
