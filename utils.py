# class RepetitionSystemUtils:
#     def __init__(self):
#
from random import randint


# class WrongFile(BaseException)

class WrongImportFilenameExtension(BaseException):
    pass

class Card:
    def __init__(self, card_id, front, back):
        self.front = front
        self.back = back
        self.card_id = card_id


class CardQueue:
    def __init__(self, queue):
        self.queue = queue
        self.used_cards = []
        self.cur_card = None

    # def add_card(self, card):
    #     self.queue.append(card)

    def get_next_card(self) -> Card | None:
        if self.queue:
            self.cur_card = self.queue.pop(0)
            return self.cur_card
        return None

    def re_queue_card(self, memory_level: str):
        queue_len = len(self.queue)
        memory_level = memory_level.lower()
        if memory_level == "again":
            insert_position = randint(1, max(2, min(queue_len, 5)))
        elif memory_level == "hard":
            insert_position = randint(min(queue_len // 4, queue_len), min(queue_len // 2, queue_len))
        elif memory_level == "good":
            insert_position = randint(min(queue_len // 2, queue_len), min(queue_len * 3 // 4, queue_len))
        elif memory_level == "easy":
            insert_position = randint(min(queue_len * 3 // 4, queue_len), queue_len)

        # # Находим индекс карточки в текущей очереди и удаляем ее
        # try:
        #     current_index = self.queue.index(card)
        #     self.queue.pop(current_index)
        # except ValueError:
        #     # Карточка могла быть уже удалена
        #     pass

        self.queue.insert(insert_position, self.cur_card)

    def __len__(self):
        return len(self.queue)


INFINITY = 1e9  # float("inf")
STRINGS = {
    "app_title": "Repetition system",
    "messages": {
        "welcome": "Welcome to My Application!",
        "error": "An error occurred. Please try again later."
    },
    "labels": {
        "dialog_label_deck": "Name of the new deck:",
        "deck_exist": {
            "title": "Be careful",
            "message": "This deck is already exist."
        },
        "deck_not_selected": {
            "title": "Draw attention",
            "message": "No deck is selected. Please select one."
        },
        "no_decks": {
            "title": "Draw attention",
            "message": "No deck is available for selecting. For proceeding, please, create one"
        }
    },
    "errors": {
        "apkg_not_supported": "This filename extension isn't supported at the moment",
        "unsupported_filename_extension": "Unsupported filename extension"
    }
}

import_separator_symbols = {
    "Tabulation": '\t',
    "Vertical bar": '|',
    "Semicolon": ';',
    "Colon": ':',
    "Comma": ',',
    "Whitespace": ' '
}

# import_separator_symbols = {
#     "Comma (,)" : ",",
#     "Semicolon (;)" : ";",
#     "Tab (\\t)" : "\t",
#     "Space ( )" : " ",
#     "Pipe (|)" : "|"
# }