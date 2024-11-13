from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QApplication
from PyQt6.QtCore import Qt

class FlashcardPage(QWidget):
    def __init__(self, card_data, parent=None):
        super().__init__(parent)

        self.card_data = card_data
        self.current_card_index = 0
        self.showing_front = True

        self.layout = QVBoxLayout()
        self.question_label = QLabel()
        self.question_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.question_label.setWordWrap(True)
        self.answer_label = QLabel()
        self.answer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.answer_label.setWordWrap(True)
        self.answer_label.hide()

        self.flip_button = QPushButton("Show Answer")
        self.flip_button.clicked.connect(self.flip_card)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_card)

        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.previous_card)


        self.layout.addWidget(self.question_label)
        self.layout.addWidget(self.answer_label)
        self.layout.addWidget(self.flip_button)
        self.layout.addWidget(self.prev_button)
        self.layout.addWidget(self.next_button)
        self.setLayout(self.layout)

        self.show_card()


    def show_card(self):
        if 0 <= self.current_card_index < len(self.card_data):
            card = self.card_data[self.current_card_index]
            if self.showing_front:
                self.question_label.setText(card.get("question", "No Question"))
                self.answer_label.hide()
                self.flip_button.setText("Show Answer")

            else:
                self.answer_label.setText(card.get("answer", "No Answer"))
                self.answer_label.show()
                self.flip_button.setText("Show Question")


        else:
            self.question_label.setText("No cards left")
            self.answer_label.hide()
            self.flip_button.setText("Show Answer")



    def flip_card(self):
        self.showing_front = not self.showing_front
        self.show_card()

    def next_card(self):
        self.current_card_index += 1
        self.showing_front = True
        self.show_card()

    def previous_card(self):
         if self.current_card_index > 0:
            self.current_card_index -= 1
            self.showing_front = True
            self.show_card()





if __name__ == "__main__":
    app = QApplication([])
    card_data = [
        {"question": "What is the capital of France?", "answer": "Paris"},
        {"question": "What is the highest mountain in the world?", "answer": "Mount Everest"},
        {"question": "What is the smallest country in the world?", "answer": "Vatican City"},
    ]
    window = FlashcardPage(card_data)
    window.show()
    app.exec()