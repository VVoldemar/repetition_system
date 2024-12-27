# from PyQt6.QtWidgets import QWidget, QApplication, QDialogButtonBox, QDialog
#
# from filter_window import Ui_Form
# from PyQt6 import QtCore, QtGui, QtWidgets
# from db import Database
#
# class DeckChoiceWidget(QDialog, Ui_Form):
#     def __init__(self):
#         super().__init__()
#         self.setupUi(self)
#         decks = db.get_decks()
#         self.decksLW.addItems(decks)
#         self.deck = ''
#
#         self.decksLW.itemDoubleClicked.connect(self.item_selected)
#
#
#     def item_selected(self):
#         self.deck = self.decksLW.currentItem().text()
#         self.close()
#         return self.deck
#
#
#
# if __name__ == '__main__':
#     import sys
#     db = Database('sr_db1.sqlite')
#     db.create_tables()
#     app = QApplication(sys.argv)
#     wd = DeckChoiceWidget()
#     wd.show()
#     sys.excepthook = lambda cls, exception, traceback: sys.__excepthook__(cls, exception, traceback)
#     res = wd.exec()
#     print(res)
#     sys.exit(res)
#     # sys.exit(app.exec())


from PyQt6.QtWidgets import QWidget, QApplication, QDialogButtonBox, QDialog, QLineEdit, QListWidgetItem
from PyQt6 import QtCore
from filter_window import Ui_Form
from db import Database

class DeckChoiceWidget(QDialog, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.db = Database('sr_db1.sqlite')
        self.decks = self.db.get_decks()
        self.all_items = [QListWidgetItem(deck) for deck in self.decks]  # Сохраняем все элементы
        self.decksLW.addItems([item.text() for item in self.all_items])  # Отображаем их в виджете
        self.deck = ''

        self.decksLW.itemDoubleClicked.connect(self.item_selected)
        self.filterValueTE.textChanged.connect(self.filter_items) # Подключаем сигнал изменения текста к фильтру

        self.buttonBox.accepted.connect(self.accept) # Подключам Accept к кнопке OK
        self.buttonBox.rejected.connect(self.reject) # Подключам Reject к кнопке Cancel

    def filter_items(self, text):
        """Фильтрует элементы списка на основе введенного текста."""
        self.decksLW.clear()
        if not text:
            self.decksLW.addItems([item.text() for item in self.all_items])
            return

        filtered_items = [item for item in self.all_items if text.lower() in item.text().lower()]
        self.decksLW.addItems([item.text() for item in filtered_items])

    def item_selected(self):
        """Обрабатывает выбор элемента двойным кликом."""
        self.deck = self.decksLW.currentItem()
        self.accept() # Закрываем окно с результатом

    def accept(self):
        if self.decksLW.currentItem():
            self.deck = self.decksLW.currentItem()
        super().accept()

    def get_selected_deck(self):
        """Возвращает выбранный элемент или None, если ничего не выбрано"""
        return self.deck

if __name__ == '__main__':
    import sys
    # db = Database('sr_db1.sqlite')
    # db.create_tables()
    app = QApplication(sys.argv)
    wd = DeckChoiceWidget()
    wd.show()
    res = wd.exec()
    if res == QDialog.DialogCode.Accepted:
        selected_deck = wd.get_selected_deck()
        if selected_deck:
            print(f"Выбранная колода: {selected_deck.text()}")
        else:
            print("Колода не выбрана.")
    sys.excepthook = lambda cls, exception, traceback: sys.__excepthook__(cls, exception, traceback)
    res = app.exec()
    # db.close()
    sys.exit(res)