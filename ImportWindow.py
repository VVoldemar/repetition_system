import csv

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox, QComboBox, QDialog

from db import Database
from import_page import Ui_Form
from utils import import_separator_symbols
from DeckChoiceWindow import DeckChoiceWidget

class ImportWindow(QDialog, Ui_Form):
    def __init__(self, parent=None, db: Database = None, file_path=""):
        super().__init__(parent)
        self.setupUi(self)
        self.db = db
        self.setModal(True)
        self.file_path = file_path
        self.comboBox.currentIndexChanged.connect(self.update_table_preview)
        # self.comboBox_2.clicked.connect(self.open_deck_choice_window)
        self.comboBox_2.showPopup = self.open_deck_choice_window

        self.pushButton.clicked.connect(self.import_cards)

        self.first_line = []
        # self.comboBox_2.setEditable(True)
        # self.tableView.setE

        # self.comboBox.setEditable(True)
        # self.comboBox.model().item(0).setEnabled(False)
        # self.comboBox.lineEdit().setPlaceholderText("Select an option")
        # self.comboBox.lineEdit().setEnabled(False)
        self.comboBox.setCurrentIndex(-1)

    def update_table_preview(self):
        try:
            text = self.comboBox.currentText()
            if text in import_separator_symbols:
                delimiter = import_separator_symbols[text]
                data = self.read_csv(delimiter)
                model = self.create_model(data)

                self.data = data
                print(data)

                self.tableView.setModel(model)
                self.update_sides(data[0])
                # table_view.show()
        except UnicodeError:
            QMessageBox.critical(None, "Error", 'Unsupported encoding. Change it to utf-8', QMessageBox.StandardButton.Ok)

    def create_model(self, data):
        model = QStandardItemModel()

        for row_data in data:
            row = []
            for item_data in row_data:
                item = QStandardItem(item_data)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                row.append(item)
            model.appendRow(row)

        return model

    def read_csv(self, delimiter):
        data = []
        with open(self.file_path, 'r', encoding='utf-8') as file:  # Укажите правильную кодировку
            reader = csv.reader(file, delimiter=delimiter)
            for row in reader:
                if any(row):
                    data.append(row)
        return data

    def open_deck_choice_window(self):
        deck_choice_widget = DeckChoiceWidget()
        result = deck_choice_widget.exec()
        if result: #  QDialog.DialogCode.Accepted:
            selected_deck = deck_choice_widget.get_selected_deck()
            if selected_deck:
                self.comboBox_2.setItemText(0, selected_deck.text())

    def update_sides(self, first_line):
        if not first_line:
            QMessageBox.warning(self, "Error", "CSV file is empty or invalid")
            return

        self.comboBox_3.clear()
        self.comboBox_4.clear()

        formatted_line = [f"{i + 1}: {e}" for i, e in enumerate(first_line)]

        self.comboBox_3.addItems(formatted_line)
        self.comboBox_4.addItems(formatted_line)

    def import_cards(self):
        cboxes = [eval(f"self.comboBox_{i}") for i in range(2, 5)]
        if all(list(map(QComboBox.currentText, cboxes))):
            self.db.add_cards(self.comboBox_2.currentText(), [list(map(str.strip, item)) for item in self.data])
            # self.cur = [list(map(str.strip, item)) for item in self.data]
            # print(self.cur)
        else:
            QMessageBox.warning(self, "Error", "Not all required fields are filled")
            return

        self.close()
        # print(*[type(e) for e in cboxes])
        # print(list(map(QComboBox.currentText, cboxes)))
        # if all(list(map(lambda cbox: cbox)))
        #     self.comboBox_3.currentText()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    db = Database('sr_db1.sqlite')
    db.create_tables()
    # wd = ImportWindow()
    wd = ImportWindow(None, db, r"C:\Users\Vladimir\Documents\Учёные.csv")
    wd.show()
    sys.excepthook = lambda cls, exception, traceback: sys.__excepthook__(cls, exception, traceback)
    sys.exit(app.exec())