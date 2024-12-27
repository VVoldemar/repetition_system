import sqlite3
import datetime

from utils import Card


class Database:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def create_tables(self, ):
        self.cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS decks (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT,
              creation_date DATE,
              UNIQUE(name)
            );''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS boxes (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              interval INTEGER
            );''')

        self.cursor.execute('''
            INSERT OR IGNORE INTO boxes (interval) VALUES
            (0),
            (0),
            (0),
            (1),
            (3),
            (7),
            (10),
            (14),
            (20),
            (30);''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cards (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              deck_id INTEGER,
              -- box_id INTEGER,
              front_side TEXT,
              back_side TEXT,
              FOREIGN KEY(deck_id) REFERENCES decks(id)
              -- FOREIGN KEY(box_id) REFERENCES boxes(id)
            );''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_id INTEGER NOT NULL,
            deck_id INTEGER NOT NULL,
            box_id INTEGER NOT NULL,
            queue_position INTEGER NOT NULL,
            last_revision date DATE,
            FOREIGN KEY (card_id) REFERENCES cards(id), -- Предполагаем, что есть таблица 'cards' с информацией о карточках
            FOREIGN KEY (deck_id) REFERENCES decks(id),
            FOREIGN KEY (box_id) REFERENCES boxes(id)
            );
            ''')
        self.conn.commit()

    # def get_cards_for_review(self, deck_name):
    #     return self.cursor.execute('''
    #         SELECT * FROM cards
    #         WHERE deck_id = (
    #         SELECT id FROM decks WHERE name = ?
    #         ) AND (last_revision < DATE(CURRENT_DATE) - (
    #         SELECT interval FROM boxes WHERE id = cards.box_id
    #         ) OR (SELECT interval FROM boxes WHERE id = cards.box_id) < 1)
    #     ''', deck_name).fetchall()

    def add_deck(self, deck_name):
        """Insert a deck into the database"""
        try:
            self.cursor.execute('''
                INSERT INTO decks (name, creation_date) VALUES (?, date(?))
            ''', (deck_name, datetime.date.today().strftime('%Y-%m-%d')))
            self.conn.commit()
        except sqlite3.Error as error:
            print(error.sqlite_errorcode, error.sqlite_errorname, error.__str__(), sep='\n', end='\n')


    def delete_deck(self, deck_name):
        """Delete a deck from the database"""
        try:
            self.cursor.execute('''
                DELETE FROM cards WHERE cards.deck_id = (SELECT id FROM decks WHERE name = ?)
            ''', (deck_name, ))
            self.cursor.execute('''
                DELETE FROM decks WHERE decks.name = ?
            ''', (deck_name, ))
            self.conn.commit()
        except sqlite3.Error as error:
            print(error.sqlite_errorcode, error.sqlite_errorname, error.__str__(), sep='\n', end='\n')


    def add_card(self, deck_name, front, back):
        self.cursor.execute('''
            INSERT INTO cards (deck_id, front_side, back_side) VALUES ((
            SELECT id FROM decks
            WHERE name = ?
            ), ?, ?) 
            RETURNING id, deck_id
        ''', (deck_name, front, back))

        card_id, deck_id = self.cursor.fetchone()

        print(card_id)

        self.cursor.execute('''
            INSERT INTO queue (card_id, deck_id, box_id, queue_position, last_revision) VALUES (
            ?, ?, 1, (SELECT IFNULL(MAX(queue_position), 0) + 1
                      FROM queue
                      WHERE deck_id = ? AND box_id = 1), date()
             )
             RETURNING queue_position
        ''', (card_id, deck_id, deck_id))

        queue_position = self.cursor.fetchone()[0]
        print(queue_position)

        # card_id = self.cursor.lastrowid

        self.conn.commit()

    def add_cards(self, deck_id, cards: tuple[str, str]):
        """Adds cards to the database from import cards"""
        for card in cards:
            self.add_card(deck_id, card[0], card[1])

    def delete_card(self, deck_id, box_id):
        self.cursor

    def get_card(self, deck_id, box_id):
        self.cursor

    def get_cards(self, deck_id, box_id):
        self.cursor

    def get_decks(self):
        """Returns list of string of decks ordered by name"""
        return [item[0] for item in self.cursor.execute('''
        SELECT name FROM decks
        ORDER BY name
        ''').fetchall()]

    def get_queue(self, deck_name):
        queue = self.cursor.execute('''
            SELECT
                c.id,
                c.front_side, 
                c.back_side
            FROM 
                cards c
            JOIN 
                queue q 
            ON 
                c.id = q.card_id
            JOIN 
                boxes b 
            ON 
                q.box_id = b.id
            JOIN 
                decks d 
            ON 
                q.deck_id = d.id
            WHERE 
                date(q.last_revision, '+' || b.interval || ' day') <= date()
                AND d.name = ?
            ORDER BY 
                b.interval, 
                q.queue_position; 
        ''', (deck_name, )).fetchall()

        return [Card(*item) for item in queue]

    def get_interval(self, card_id: int):
        return self.cursor.execute('''
            SELECT boxes.interval FROM boxes
            JOIN queue q ON q.box_id = boxes.id
            WHERE q.card_id = ?
        ''', (card_id, )).fetchone()[0]

    def update_increase_box(self, card_id: int, boxes_shift: int):
        self.cursor.execute('''
            UPDATE queue
            SET box_id = (
                SELECT MIN(MAX(queue.box_id + ?, (SELECT MIN(boxes.id) FROM boxes)), (SELECT MAX(boxes.id) FROM boxes))
            )
            WHERE queue.card_id = ?;
        ''', (boxes_shift, card_id))
        self.conn.commit()

    def update_revision_date(self, card_id: int):
        self.cursor.execute('''
            UPDATE queue
            SET last_revision = date()
            WHERE queue.card_id = ?;
        ''', (card_id, ))

    def update_queue(self, new_queue: list[Card]):
        for i, item in enumerate(new_queue):
            self.cursor.execute('''
                UPDATE queue
                SET queue_position = ?
                WHERE card_id = ?
            ''', (i + 1, new_queue[i].card_id))

    def close(self):
        self.conn.close()