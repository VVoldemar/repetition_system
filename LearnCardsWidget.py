import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox, QDialog

from DeckChoiceWindow import DeckChoiceWidget
from db import Database
from learn_cards_widget import Ui_Form

from utils import STRINGS, CardQueue, INFINITY


class LearnCardsWidget(QWidget, Ui_Form):
    def __init__(self, db: Database=None, deck_name=""):
        super().__init__()
        self.setupUi(self)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        # self.setModal(True)

        self.deck_name = deck_name
        self.update_label(self.deck_name)
        self.db = db
        self.queue = CardQueue([])
        self.load_queue()
        # self.deckNameL.returnPressed.connect(self)
        self.back_mode(False)
        self.display_card()

        self.decksViewBtn.clicked.connect(self.open_deck_choice_window)

        self.complexBtn.clicked.connect(self.complexity_handler)
        self.hardBtn.clicked.connect(self.complexity_handler)
        self.normalBtn.clicked.connect(self.complexity_handler)
        self.easyBtn.clicked.connect(self.complexity_handler)

        self.showAnswerBtn.clicked.connect(lambda: self.back_mode(True))
        self.setWindowTitle('Deck learning')

    def load_queue(self):
        self.queue = CardQueue(self.db.get_queue(self.deck_name))

    def display_card(self):
        self.frontTB.clear()
        self.backTB.clear()
        self.interaction_mode(True)
        # self.check_card_available()
        cur_card = self.queue.get_next_card()
        if cur_card is None:
            self.interaction_mode(False)
            QMessageBox.warning(self, 'Warning', 'No remaining card')
            return
        self.frontTB.setHtml(cur_card.front)
        self.backTB.setHtml(cur_card.back)
        self.back_mode(False)

    def check_card_available(self):
        if not len(self.queue):
            return False
        return True

    def complexity_handler(self):
        if self.check_card_available() or self.queue.cur_card is not None:
            sender = self.sender()
            cur_card_id = self.queue.cur_card.card_id

            if sender:
                print(f"Button clicked! Sender object: {sender}")
                print(f"Sender's object name: {sender.objectName()}")
                print(f"Sender's text: {sender.text()}")

            match sender.text().lower():
                case "again":
                    self.db.update_increase_box(cur_card_id, -int(INFINITY))
                case "hard":
                    self.db.update_increase_box(cur_card_id, -1)
                case "good":
                    self.db.update_increase_box(cur_card_id, 1)
                case "easy":
                    self.db.update_increase_box(cur_card_id, 2)

            self.db.update_revision_date(cur_card_id)

            if int(self.db.get_interval(cur_card_id)) == 0:
                self.queue.re_queue_card(sender.text().lower())
            else:
                self.queue.used_cards.append(self.queue.cur_card)

            self.queue.cur_card = None

        self.display_card()


    def interaction_mode(self, mode: bool):
        self.showAnswerBtn.setEnabled(mode)
        self.frontTB.setEnabled(mode)
        if not mode:
            self.showAnswerBtn.setToolTip("Please, select non-empty deck")
            self.frontTB.setToolTip("Please, select non-empty deck")

    def back_mode(self, mode: bool):
        self.complexityWidget.setVisible(mode)
        self.backTB.setVisible(mode)
        self.showAnswerBtn.setVisible(not mode)

    def open_deck_choice_window(self):
        deck_choice_widget = DeckChoiceWidget()
        result = deck_choice_widget.exec()
        if result:  # QDialog.DialogCode.Accepted:
            selected_deck = deck_choice_widget.get_selected_deck()
            if selected_deck:
                self.update_db()
                self.deck_name = selected_deck.text()
                self.update_label(self.deck_name)
                self.back_mode(False)
                self.load_queue()
                self.display_card()

    def update_label(self, new_deck_name):
        self.deckNameL.setText(f"Deck: {new_deck_name}")

    def update_db(self):
        self.db.update_queue(self.queue.queue + self.queue.used_cards)
        self.queue.cur_card = None

    def closeEvent(self, event):
        ...

        # if reply == QMessageBox.StandardButton.Yes:
        #     # Выполняем действия перед закрытием (например, сохраняем данные)
        #     self.save_data()
        #     event.accept()  # Закрываем окно
        # else:
        #     event.ignore()  # Отменяем закрытие окна


if __name__ == '__main__':
    db = Database('sr_db1.sqlite')
    db.create_tables()
    app = QApplication(sys.argv)
    ex = LearnCardsWidget(db, deck_name='1')
    ex.show()
    sys.excepthook = lambda cls, exception, traceback: sys.__excepthook__(cls, exception, traceback)
    res = app.exec()
    db.close()
    sys.exit(res)