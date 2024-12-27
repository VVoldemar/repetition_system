import sys
import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, \
    QSpacerItem, QSizePolicy, QFileDialog, QMessageBox, QErrorMessage, QListWidgetItem

from CardAddWindow import CardAddWindow
from LearnCardsWidget import LearnCardsWidget
# from example.decks_displaying_example import DeckListWidget
from db import Database
from main_window import Ui_MainWindow
from ImportWindow import ImportWindow
from DialogWidget import DialogWidget

from utils import STRINGS

class MWindow(QWidget, Ui_MainWindow):
    def __init__(self, db):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Main Window")
        self.db = db

        # self.stacked_widget = QStackedWidget()
        # self.setCentralWidget(self.stacked_widget)
        # self.decks_page = DeckListWidget()
        # self.stacked_widget.addWidget(self.decks_page)

        self.setWindowTitle('Repetition System')

        self.deckAddButton.clicked.connect(self.add_deck)
        self.cardAddButton.clicked.connect(self.add_card)
        self.importCardsButton.clicked.connect(self.select_import_file)
        self.deleteDeckButton.clicked.connect(self.delete_deck)
        self.deckWidget.itemDoubleClicked.connect(self.item_selected)

        self.deckWidget.setSortingEnabled(True)
        self.display_decks()

    def display_decks(self):
        decks = db.get_decks()
        if not len(decks):
            self.deckWidget.setToolTip("Add deck by clicking on the 'Add deck' button")
        self.deckWidget.addItems(decks)

    def add_card(self):
        card_add_window = CardAddWindow(self, db)
        res = card_add_window.exec()
        if res:
            ...
        else:
            print("dsgfvjndngjrdfogk")


    def add_deck(self):
        deckDialog = DialogWidget(self, STRINGS["labels"]["dialog_label_deck"])
        if deckDialog.exec():  # == QDialog.DialogCode.Accepted
            # print("Hello", deckDialog.lineEdit.text())
            if deckDialog.lineEdit.text() in db.get_decks():
                QMessageBox.warning(self, STRINGS["labels"]["deck_exist"]["title"], STRINGS["labels"]["deck_exist"]["message"])
                return
            db.add_deck(deckDialog.lineEdit.text())
            item = QListWidgetItem(deckDialog.lineEdit.text())
            self.deckWidget.addItem(item)

    def delete_deck(self):
        # deck_dialog = DialogWidget(self, STRINGS[""])
        # self.deckWidget.removeItem(self.deckWidget.selectedItems())
        # if self.deckWidget.selectedItems():
            # self.deckWidget.selectedItems()
            # map(self.deckWidget.removeItemWidget, self.deckWidget.selectedItems())
            # self.deckWidget.removeItemWidget(self.deckWidget.selectedItems()[0])
        selected_decks = self.deckWidget.selectedItems()
        if not len(selected_decks) and len(db.get_decks()):
            QMessageBox.information(self, STRINGS["labels"]["deck_not_selected"]["title"],
                                    STRINGS["labels"]["deck_not_selected"]["message"])
            return
        if not len(selected_decks) and not len(db.get_decks()):
            QMessageBox.warning(self, STRINGS["labels"]["no_decks"]["title"],
                                STRINGS["labels"]["no_decks"]["message"])
            return
        for deck in selected_decks:
            db.delete_deck(deck.text())
            self.deckWidget.takeItem(self.deckWidget.currentRow())

    def item_selected(self):
        self.learn_window = LearnCardsWidget(self.db, self.deckWidget.currentItem().text())
        self.learn_window.show()
    def select_import_file(self):
        # options = QFileDialog.options()
        # options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите CSV файл ", "",
                                                   "CSV файлы (*.csv);;Anki Flashcard Deck(*.apkg);;Все файлы (*)")
        if file_path:
            print(file_path)

            match os.path.splitext(file_path)[1]:
                case '.csv':
                    self.IW = ImportWindow(self, self.db, file_path)
                    self.IW.show()
                case '.apkg':
                    QMessageBox.critical(None, "Error", STRINGS["errors"]["apkg_not_supported"],
                                         QMessageBox.StandardButton.Ok)
                case _:
                    QMessageBox.critical(None, "Error", STRINGS["errors"]["unsupported_filename_extension"],
                                         QMessageBox.StandardButton.Ok)

        print(os.path.splitext(file_path)[1])

    def closeEvent(self, event):
        # Диалог подтверждения закрытия
        reply = QMessageBox.question(
            self,
            "Подтверждение закрытия",
            "Вы действительно хотите закрыть окно?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Выполняем действия перед закрытием (например, сохраняем данные)
            self.save_data()
            event.accept()  # Закрываем окно
        else:
            event.ignore()  # Отменяем закрытие окна

    def save_data(self):
        print("Данные сохранены!")  # Здесь можно добавить код для сохранения данных


if __name__ == '__main__':
    db = Database('sr_db1.sqlite')
    db.create_tables()
    app = QApplication(sys.argv)
    ex = MWindow(db)
    ex.show()
    sys.excepthook = lambda cls, exception, traceback: sys.__excepthook__(cls, exception, traceback)
    res = app.exec()
    db.close()
    sys.exit(res)