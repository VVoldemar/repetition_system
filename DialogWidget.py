from PyQt6.QtWidgets import QWidget, QApplication, QDialogButtonBox, QDialog

from dialog import Ui_Form
from PyQt6 import QtCore, QtGui, QtWidgets

class DialogWidget(QDialog, Ui_Form):
    def __init__(self, parent=None, label_text=""):
        super().__init__(parent)
        self.setModal(True)
        self.setupUi(self, label_text)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)



if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    wd = DialogWidget("Enter your name")
    res = wd.exec()
    if res:
        print("Hello", wd.lineEdit.text())
    sys.excepthook = lambda cls, exception, traceback: sys.__excepthook__(cls, exception, traceback)
    # sys.exit(app.exec())