import requests
from PyQt6.QtCore import Qt, QUrl, QBuffer, QIODevice
from PyQt6.QtGui import (QTextCharFormat, QFont, QColor, QTextBlockFormat,
                         QIcon, QAction, QImage, QImageReader, QTextImageFormat,
                         QGuiApplication, QTextDocument, QTextCursor)
from PyQt6.QtWidgets import (QApplication, QWidget, QMessageBox, QColorDialog,
                             QTextEdit, QFileDialog, QMenu, QDialog, QVBoxLayout,
                             QHBoxLayout, QLabel, QSpinBox, QPushButton, QComboBox,
                             QToolBar, QButtonGroup, QProgressBar, QInputDialog, QMainWindow)

from DeckChoiceWindow import DeckChoiceWidget
from add_card_widget import Ui_Form
import base64


class ImagePropertiesDialog(QDialog):
    def __init__(self, parent=None, current_width=None, current_height=None):
        super().__init__(parent)
        self.setWindowTitle("Image Properties")
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Размеры
        size_group = QHBoxLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 2000)
        self.width_spin.setValue(current_width if current_width else 200)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 2000)
        self.height_spin.setValue(current_height if current_height else 200)

        size_group.addWidget(QLabel("Width:"))
        size_group.addWidget(self.width_spin)
        size_group.addWidget(QLabel("Height:"))
        size_group.addWidget(self.height_spin)
        layout.addLayout(size_group)

        # Выравнивание
        align_group = QHBoxLayout()
        self.alignment_combo = QComboBox()
        self.alignment_combo.addItems(["Left", "Center", "Right"])
        align_group.addWidget(QLabel("Alignment:"))
        align_group.addWidget(self.alignment_combo)
        layout.addLayout(align_group)

        # Подпись
        caption_group = QHBoxLayout()
        self.caption_edit = QTextEdit()
        self.caption_edit.setMaximumHeight(50)
        caption_group.addWidget(QLabel("Caption:"))
        caption_group.addWidget(self.caption_edit)
        layout.addLayout(caption_group)

        # Кнопки
        buttons = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        layout.addLayout(buttons)


class CardAddWindow(QDialog, QMainWindow, Ui_Form):
    def __init__(self, parent=None, db=None):
        super().__init__(parent)
        self.setupUi(self)
        # self.setWindowFlag(QMainWindow)
        self.showMaximized()

        self.db = db
        self.setModal(True)

        self.active_text_edit = None
        self.cancelled = False

        # Подключаем обработчики событий, сохраняя стандартное поведение
        self.frontTE.mousePressEvent = self.front_mouse_press_event
        self.backTE.mousePressEvent = self.back_mouse_press_event

        # Разрешаем drop для обоих текстовых полей
        self.frontTE.setAcceptDrops(True)
        self.backTE.setAcceptDrops(True)

        # Переопределяем обработчики событий drag&drop
        self.frontTE.dragEnterEvent = self.dragEnterEvent
        self.frontTE.dropEvent = self.dropEvent
        self.backTE.dragEnterEvent = self.dragEnterEvent
        self.backTE.dropEvent = self.dropEvent

        self.active_text_edit = self.frontTE

        # Вызов пользовательского контекстного меню в текстовых полях
        self.frontTE.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.frontTE.customContextMenuRequested.connect(self.show_context_menu)

        self.backTE.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.backTE.customContextMenuRequested.connect(self.show_context_menu)

        # Подключение кнопок форматирования текста
        self.boldButton.clicked.connect(self.make_bold)
        self.boldButton.setShortcut("Ctrl+B")
        self.boldButton.setToolTip("Bold (Ctrl + B)")

        self.italicButton.clicked.connect(self.make_italic)
        self.italicButton.setShortcut("Ctrl+I")
        self.italicButton.setToolTip("Italic (Ctrl + I)")

        self.underlineButton.clicked.connect(self.make_underline)
        self.underlineButton.setShortcut("Ctrl+U")
        self.underlineButton.setToolTip("Underline (Ctrl + U)")

        self.clearFormattingButton.clicked.connect(self.clear_formatting)
        self.clearFormattingButton.setShortcut("Ctrl+R")
        self.clearFormattingButton.setToolTip("Clear formatting (Ctrl + R)")

        self.textSizeSB.setValue(12)
        self.textSizeSB.valueChanged.connect(self.change_font_size)

        self.colorButton.clicked.connect(self.change_font_color)
        self.colorButton.setShortcut("F7")
        self.colorButton.setToolTip("Change color (F7)")

        # Создание панели инструментов для изображений
        # image_toolbar = self.create_image_toolbar()
        # self.toolbar.layout().addWidget(image_toolbar)
        # self.toolbar.layout().a

        # Добавляем прогресс-бар
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setVisible(False)
        self.toolbar.layout().addWidget(self.progress_bar)

        # Создаем меню для работы с изображениями
        self.image_menu = QMenu("Image", self)

        self.insert_image_action = QAction("Insert Image", self)
        self.insert_image_action.setShortcut("Ctrl+Shift+I")
        self.insert_image_action.setToolTip("Ctrl+Shift+I")
        self.insert_image_action.triggered.connect(self.insert_image)

        self.insert_url_image_action = QAction("Insert Image from URL", self)
        self.insert_url_image_action.setShortcut("Ctrl+Shift+U")
        self.insert_url_image_action.triggered.connect(self.insert_image_from_url)

        self.optimize_all_action = QAction("Optimize All Images", self)
        self.optimize_all_action.setShortcut("Ctrl+Shift+O")
        self.optimize_all_action.triggered.connect(self.optimize_all_images)

        self.image_menu.addAction(self.insert_image_action)
        self.image_menu.addAction(self.insert_url_image_action)
        self.image_menu.addAction(self.optimize_all_action)

        self.image_menu.addSeparator()
        self.frontTE.addAction(self.image_menu.menuAction())
        self.backTE.addAction(self.image_menu.menuAction())

        # Добавляем обработку изменений в буфере обмена
        QApplication.clipboard().dataChanged.connect(self.handle_clipboard_change)

        # Действие для очистки форматирования
        # self.clear_format_action = QAction(QIcon("example/deck_icon.svg"), "Очистить форматирование", self)
        self.clear_format_action = QAction("Очистить форматирование", self)
        self.clear_format_action.setShortcut("Ctrl+Shift+Space")
        self.clear_format_action.triggered.connect(self.clear_formatting)
        self.toolbar.addAction(self.clear_format_action)

        self.pushButton.clicked.connect(self.open_deck_choice_window)
        # self.loadButton.clicked.connect(self.load_document)
        self.buttonBox.accepted.connect(self.add_card)
        self.buttonBox.rejected.connect(self.rejected)

        self.setWindowTitle('Rich Text Editor')
        self.show()

    # Методы для работы с текстом
    def front_mouse_press_event(self, event):
        self.set_active_text_edit(self.frontTE)
        QTextEdit.mousePressEvent(self.frontTE, event)

    def back_mouse_press_event(self, event):
        self.set_active_text_edit(self.backTE)
        QTextEdit.mousePressEvent(self.backTE, event)

    def set_active_text_edit(self, text_edit):
        self.active_text_edit = text_edit
        self.active_text_edit.setFocus()

    def open_deck_choice_window(self):
        deck_choice_widget = DeckChoiceWidget()
        result = deck_choice_widget.exec()
        if result:  # QDialog.DialogCode.Accepted:
            selected_deck = deck_choice_widget.get_selected_deck()
            if selected_deck:
                self.pushButton.setText(selected_deck.text())

    def make_bold(self):
        if self.active_text_edit:
            cursor = self.active_text_edit.textCursor()
            if not cursor.hasSelection():
                return

            fmt = cursor.charFormat()
            fmt.setFontWeight(
                QFont.Weight.Normal if fmt.fontWeight() == QFont.Weight.Bold else QFont.Weight.Bold
            )
            cursor.mergeCharFormat(fmt)

    def make_italic(self):
        if self.active_text_edit:
            cursor = self.active_text_edit.textCursor()
            if not cursor.hasSelection():
                return

            fmt = cursor.charFormat()
            fmt.setFontItalic(not fmt.fontItalic())
            cursor.mergeCharFormat(fmt)

    def make_underline(self):
        if self.active_text_edit:
            cursor = self.active_text_edit.textCursor()
            if not cursor.hasSelection():
                return

            fmt = cursor.charFormat()
            fmt.setFontUnderline(not fmt.fontUnderline())
            cursor.mergeCharFormat(fmt)

    def clear_formatting(self):
        if self.active_text_edit:
            cursor = self.active_text_edit.textCursor()
            if not cursor.hasSelection():
                return

            fmt = QTextCharFormat()
            fmt.setFontPointSize(12)
            cursor.setCharFormat(fmt)

    def change_font_size(self, size):
        if self.active_text_edit:
            cursor = self.active_text_edit.textCursor()
            if not cursor.hasSelection():
                return

            fmt = cursor.charFormat()
            fmt.setFontPointSize(size)
            cursor.mergeCharFormat(fmt)

    def change_font_color(self):
        if self.active_text_edit:
            cursor = self.active_text_edit.textCursor()
            if not cursor.hasSelection():
                return

            color = QColorDialog.getColor()
            if color.isValid():
                fmt = cursor.charFormat()
                fmt.setForeground(color)
                cursor.mergeCharFormat(fmt)

    # Методы для работы с изображениями
    def insert_image(self):
        if self.active_text_edit:
            file_name, _ = QFileDialog.getOpenFileName(
                self,
                "Select Image",
                "",
                "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
            )

            if file_name:
                image = QImage(file_name)
                if image.isNull():
                    QMessageBox.warning(self, "Error", "Failed to load image!")
                    return

                self.insert_image_with_properties(image)

    def insert_image_with_properties(self, image, show_dialog=True):
        if not self.active_text_edit:
            return

        if show_dialog:
            dialog = ImagePropertiesDialog(self, image.width(), image.height())
            if dialog.exec() == QDialog.DialogCode.Accepted:
                width = dialog.width_spin.value()
                height = dialog.height_spin.value()
                alignment = dialog.alignment_combo.currentText().lower()
                caption = dialog.caption_edit.toPlainText()

                # Масштабируем изображение
                if width != image.width() or height != image.height():
                    image = image.scaled(width, height,
                                         Qt.AspectRatioMode.KeepAspectRatio,
                                         Qt.TransformationMode.SmoothTransformation)

                # Вставляем изображение
                cursor = self.active_text_edit.textCursor()

                # Устанавливаем выравнивание
                block_format = QTextBlockFormat()
                if alignment == "left":
                    block_format.setAlignment(Qt.AlignmentFlag.AlignLeft)
                elif alignment == "center":
                    block_format.setAlignment(Qt.AlignmentFlag.AlignCenter)
                else:
                    block_format.setAlignment(Qt.AlignmentFlag.AlignRight)

                cursor.insertBlock(block_format)
                cursor.insertImage(image)

                # Добавляем подпись, если она есть
                if caption:
                    cursor.insertBlock(block_format)
                    cursor.insertText(caption)
        else:
            cursor = self.active_text_edit.textCursor()
            cursor.insertImage(image)

    def get_image_from_url(self, url):
        try:
            # Fetch the image data from the URL
            response = requests.get(url)
            response.raise_for_status()  # Raise an error if the request failed

            # Create a QImage and load the binary data into it
            image = QImage()
            if image.loadFromData(response.content):
                return image, None
            else:
                return None, "Failed to load image from data."
        except requests.RequestException as e:
            return None, f"Error fetching image from URL: {e}"

    def insert_image_from_url(self):
        url, ok = QInputDialog.getText(
            self,
            "Insert Image from URL",
            "Enter image URL:"
        )

        if ok and url:
            image, error = self.get_image_from_url(url)
            if image is None:
                QMessageBox.warning(self, "Error", "Failed to load image from URL")
            else:
                self.insert_image_with_properties(image)
            # try:
            #     image = QImage(url)
            #     if not image.isNull():
            #         self.insert_image_with_properties(image)
            #     else:
            #         QMessageBox.warning(self, "Error", "Failed to load image from URL")
            # except Exception as e:
            #     QMessageBox.warning(self, "Error", f"Error loading image: {str(e)}")

    def handle_clipboard_change(self):
        clipboard = QApplication.clipboard()
        if clipboard.mimeData().hasImage():
            self.paste_image_button.setEnabled(True)
        else:
            self.paste_image_button.setEnabled(False)

    def handle_paste(self):
        if self.active_text_edit:
            clipboard = QApplication.clipboard()
            mime_data = clipboard.mimeData()

            if mime_data.hasImage():
                image = QImage(mime_data.imageData())
                if not image.isNull():
                    self.insert_image_with_properties(image)
            else:
                # Стандартная вставка текста
                self.active_text_edit.paste()

    def create_image_toolbar(self):
        image_toolbar = QToolBar("Image Tools")

        # Кнопка вставки изображения
        insert_button = QPushButton("Insert Image")
        insert_button.clicked.connect(self.insert_image)
        image_toolbar.addWidget(insert_button)

        # Кнопка вставки из буфера обмена
        self.paste_image_button = QPushButton("Paste Image")
        self.paste_image_button.clicked.connect(self.handle_paste)
        self.paste_image_button.setEnabled(False)
        image_toolbar.addWidget(self.paste_image_button)

        # Кнопки выравнивания
        align_group = QButtonGroup(self)

        align_left = QPushButton("Left")
        # align_left.setCheckable(True)
        align_left.clicked.connect(lambda: self.align_image("left"))

        align_center = QPushButton("Center")
        # align_center.setCheckable(True)
        align_center.clicked.connect(lambda: self.align_image("center"))

        align_right = QPushButton("Right")
        # align_right.setCheckable(True)
        align_right.clicked.connect(lambda: self.align_image("right"))

        align_group.addButton(align_left)
        align_group.addButton(align_center)
        align_group.addButton(align_right)

        image_toolbar.addWidget(align_left)
        image_toolbar.addWidget(align_center)
        image_toolbar.addWidget(align_right)

        return image_toolbar

    # Методы для drag&drop
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() or event.mimeData().hasImage():
            event.acceptProposedAction()

    def dropEvent(self, event):
        mime_data = event.mimeData()

        if mime_data.hasUrls():
            for url in mime_data.urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if self.is_valid_image_file(file_path):
                        image = QImage(file_path)
                        if not image.isNull():
                            self.insert_image_with_properties(image)
                            event.acceptProposedAction()
        elif mime_data.hasImage():
            image = QImage(mime_data.imageData())
            if not image.isNull():
                self.insert_image_with_properties(image)
                event.acceptProposedAction()

    def is_valid_image_file(self, file_path):
        valid_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')
        return file_path.lower().endswith(valid_extensions)

    # Методы для оптимизации изображений
    def optimize_image(self, image):
        """Оптимизация изображения"""
        # Конвертируем изображение в bytes для анализа размера
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        image.save(buffer, "PNG")
        size_before = buffer.size()

        # Если размер больше 0.25MB, сжимаем
        if size_before > 512 * 512:
            # Уменьшаем качество, сохраняя пропорции
            width = image.width()
            height = image.height()
            max_dimension = 512  # Максимальный размер стороны

            if width > height:
                if width > max_dimension:
                    width = max_dimension
                    height = int(height * max_dimension / width)
            else:
                if height > max_dimension:
                    height = max_dimension
                    width = int(width * max_dimension / height)

            image = image.scaled(width, height,
                                 Qt.AspectRatioMode.KeepAspectRatio,
                                 Qt.TransformationMode.SmoothTransformation)

        return image

    def optimize_all_images(self):
        if not self.active_text_edit:
            return

        document = self.active_text_edit.document()
        cursor = self.active_text_edit.textCursor()

        # Сохраняем текущую позицию
        original_position = cursor.position()

        cursor.movePosition(QTextCursor.MoveOperation.Start)
        total_images = 0
        optimized_images = 0
        images_info = []

        # Сначала подсчитаем количество изображений
        while not cursor.atEnd():
            image_format = cursor.charFormat().toImageFormat()
            if image_format.isValid():
                total_images += 1
                images_info.append(
                    {
                        "name": image_format.name(),
                        "position": cursor.position(),
                        "cursor": QTextCursor(cursor),
                    }
                )
            cursor.movePosition(QTextCursor.MoveOperation.NextCharacter)

        if total_images == 0:
            QMessageBox.information(self, "Info", "No images to optimize")
            return

        # Показываем прогресс-бар
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(total_images)
        self.progress_bar.setValue(0)

        # Обрабатываем все изображения, запомнив информацию о них
        for index, info in enumerate(images_info):
            cursor = info["cursor"]
            cursor.setPosition(info["position"])
            image_format = cursor.charFormat().toImageFormat()
            image = document.resource(
                QTextDocument.ResourceType.ImageResource,
                QUrl(image_format.name())
            )

            if isinstance(image, QImage):
                optimized_image = self.optimize_image(image)
                self.replace_image_with_base64(cursor, optimized_image)
                optimized_images += 1
                self.progress_bar.setValue(index + 1)
        # Восстанавливаем позицию курсора
        cursor.setPosition(original_position)

        # Скрываем прогресс-бар
        self.progress_bar.setVisible(False)

        QMessageBox.information(
            self,
            "Success",
            f"Optimized {optimized_images} of {total_images} images"
        )

    def optimize_single_image(self, cursor):
        image_format = cursor.charFormat().toImageFormat()
        if not image_format.isValid():
            return

        image = self.active_text_edit.document().resource(
            QTextDocument.ResourceType.ImageResource,
            QUrl(image_format.name())
        )

        if isinstance(image, QImage):
            optimized_image = self.optimize_image(image)
            self.replace_image_with_base64(cursor, optimized_image)
            QMessageBox.information(self, "Success", "Image optimized successfully")

    # Методы для работы с контекстным меню
    def contextMenuEvent(self, event):
        menu = self.active_text_edit.createStandardContextMenu()
        self.update_context_menu(menu)
        menu.exec(event.globalPos())

    def update_context_menu(self, menu):
        cursor = self.active_text_edit.textCursor()
        image_format = cursor.charFormat().toImageFormat()

        if image_format.isValid():
            menu.addSeparator()

            # Основные действия с изображением
            resize_action = menu.addAction("Resize Image...")
            resize_action.triggered.connect(lambda: self.resize_image(cursor))

            # Подменю выравнивания
            align_menu = menu.addMenu("Align")
            align_left = align_menu.addAction("Left")
            align_center = align_menu.addAction("Center")
            align_right = align_menu.addAction("Right")

            align_left.triggered.connect(lambda: self.align_image("left"))
            align_center.triggered.connect(lambda: self.align_image("center"))
            align_right.triggered.connect(lambda: self.align_image("right"))

            # Дополнительные действия
            menu.addSeparator()

            copy_action = menu.addAction("Copy Image")
            copy_action.triggered.connect(lambda: self.copy_image(cursor))

            save_as_action = menu.addAction("Save Image As...")
            save_as_action.triggered.connect(lambda: self.save_image_as(cursor))

            optimize_action = menu.addAction("Optimize Image")
            optimize_action.triggered.connect(lambda: self.optimize_single_image(cursor))

            info_action = menu.addAction("Image Information")
            info_action.triggered.connect(lambda: self.get_image_info(cursor))

    def get_content(self):
        """Метод для получения содержимого обоих текстовых полей"""
        front_content = self.frontTE.toHtml()
        back_content = self.backTE.toHtml()
        return self.convert_images_to_base64(front_content), self.convert_images_to_base64(back_content)

    def set_content(self, front_content="", back_content=""):
        """Метод для установки содержимого текстовых полей"""
        self.frontTE.setHtml(front_content)
        self.backTE.setHtml(back_content)

    def clear_content(self):
        """Метод для очистки содержимого обоих полей"""
        self.frontTE.clear()
        self.backTE.clear()

    def align_image(self, alignment):
        """Выравнивание выбранного изображения"""
        if not self.active_text_edit:
            return

        cursor = self.active_text_edit.textCursor()
        block_format = cursor.blockFormat()

        if alignment == "left":
            block_format.setAlignment(Qt.AlignmentFlag.AlignLeft)
        elif alignment == "center":
            block_format.setAlignment(Qt.AlignmentFlag.AlignCenter)
        elif alignment == "right":
            block_format.setAlignment(Qt.AlignmentFlag.AlignRight)

        cursor.setBlockFormat(block_format)

    def resize_image(self, cursor):
        """Изменение размера выбранного изображения"""
        image_format = cursor.charFormat().toImageFormat()
        if not image_format.isValid():
            return

        current_width = image_format.width()
        current_height = image_format.height()

        dialog = ImagePropertiesDialog(self, current_width, current_height)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_width = dialog.width_spin.value()
            new_height = dialog.height_spin.value()

            image = self.active_text_edit.document().resource(
                QTextDocument.ResourceType.ImageResource,
                QUrl(image_format.name())
            )

            if isinstance(image, QImage):
                scaled_image = image.scaled(new_width, new_height,
                                            Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation)
                self.replace_image_with_base64(cursor, scaled_image)
                self.align_image('left')

    def copy_image(self, cursor):
        """Копирование изображения в буфер обмена"""
        image_format = cursor.charFormat().toImageFormat()
        if not image_format.isValid():
            return

        image = self.active_text_edit.document().resource(
            QTextDocument.ResourceType.ImageResource,
            QUrl(image_format.name())
        )

        if isinstance(image, QImage):
            clipboard = QGuiApplication.clipboard()
            clipboard.setImage(image)
            QMessageBox.information(self, "Success", "Image copied to clipboard")

    def save_image_as(self, cursor):
        """Сохранение изображения в файл"""
        image_format = cursor.charFormat().toImageFormat()
        if not image_format.isValid():
            return

        image = self.active_text_edit.document().resource(
            QTextDocument.ResourceType.ImageResource,
            QUrl(image_format.name())
        )

        if isinstance(image, QImage):
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                "Save Image As",
                "",
                "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
            )

            if file_name:
                image.save(file_name)

    def get_image_info(self, cursor):
        """Получение информации об изображении"""
        image_format = cursor.charFormat().toImageFormat()
        if not image_format.isValid():
            return

        image = self.active_text_edit.document().resource(
            QTextDocument.ResourceType.ImageResource,
            QUrl(image_format.name())
        )

        if isinstance(image, QImage):
            # Получаем размер файла
            buffer = QBuffer()
            buffer.open(QIODevice.OpenModeFlag.WriteOnly)
            image.save(buffer, "PNG")
            size_bytes = buffer.size()

            # Форматируем размер
            if size_bytes < 512:
                size_str = f"{size_bytes} bytes"
            elif size_bytes < 512 * 512:
                size_str = f"{size_bytes / 512:.1f} KB"
            else:
                size_str = f"{size_bytes / (512 * 512):.1f} MB"

            info = (f"Dimensions: {image.width()}x{image.height()}\n"
                    f"Size: {size_str}\n"
                    f"Depth: {image.depth()} bits\n"
                    f"Format: {image.format().name}\n"
                    f"{image.size()}")

            QMessageBox.information(self, "Image Information", info)

    def show_context_menu(self, position):
        """Обработчик контекстного меню для текстовых полей."""
        text_edit = self.sender()  # Определяем, для какого текстового поля вызвано меню
        if not isinstance(text_edit, QTextEdit):
            return

        menu = text_edit.createStandardContextMenu()
        self.update_context_menu(menu)
        menu.exec(text_edit.mapToGlobal(position))

    def load_document(self):
        if self.active_text_edit:
            filename, _ = QFileDialog.getOpenFileName(self, "Open File", "", "HTML Files (*.html)")
            if filename:
                with open(filename, 'r', encoding="utf-8") as file:
                    html = file.read()
                self.active_text_edit.setHtml(html)

    def add_card(self):
        if self.pushButton.text() not in self.db.get_decks():
            QMessageBox.critical(self, "Warning", "Please, select deck")
            return
        elif not len(self.frontTE.toPlainText()) or not len(self.backTE.toPlainText()):
            print(self.frontTE.toPlainText())
            QMessageBox.critical(self, "Warning", "Please, fill both fields to add card")
            return
        front, back = self.get_content()
        self.db.add_card(self.pushButton.text(), front, back)
        self.frontTE.clear()
        self.backTE.clear()

    def rejected(self):
        self.cancelled = True
        self.reject()

    def convert_images_to_base64(self, html):
        """Конвертирует все изображения в HTML в base64 data URIs"""
        if not html:
            return html

        document = QTextDocument()
        document.setHtml(html)
        cursor = QTextCursor(document)
        new_html = ""
        prev_pos = 0

        while not cursor.atEnd():
            cursor.movePosition(QTextCursor.MoveOperation.NextCharacter)
            image_format = cursor.charFormat().toImageFormat()
            if image_format.isValid():
                # Извлекаем HTML до текущего изображения
                new_html += html[prev_pos:cursor.position() - 1]
                # Извлекаем QImage
                image = document.resource(
                    QTextDocument.ResourceType.ImageResource,
                    QUrl(image_format.name())
                )

                if isinstance(image, QImage):
                    # Конвертируем QImage в base64 data URI
                    buffer = QBuffer()
                    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
                    image.save(buffer, "PNG")
                    image_bytes = buffer.data()
                    buffer.close()

                    encoded_image = base64.b64encode(image_bytes).decode('utf-8')
                    data_uri = f"data:image/png;base64,{encoded_image}"
                    new_html += f'<img src="{data_uri}"'
                    if image_format.width() > 0 and image_format.height() > 0:
                        new_html += f' width={image_format.width()} height={image_format.height()}'
                    new_html += '/>'
                    prev_pos = cursor.position()
                else:
                    new_html += html[cursor.position() - 1:cursor.position()]

        new_html += html[prev_pos:]
        return new_html

    def replace_image_with_base64(self, cursor, image):
        """Заменяет изображение в курсоре на его base64 представление."""
        image_format = cursor.charFormat().toImageFormat()
        if not image_format.isValid():
            return

        # Конвертируем QImage в base64 data URI
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        image.save(buffer, "PNG")
        image_bytes = buffer.data()
        buffer.close()

        encoded_image = base64.b64encode(image_bytes).decode('utf-8')
        data_uri = f"data:image/png;base64,{encoded_image}"
        html = f'<img src="{data_uri}" />'
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        cursor.insertHtml(html)


if __name__ == '__main__':
    import sys
    from db import Database
    db = Database('sr_db1.sqlite')
    db.create_tables()
    app = QApplication(sys.argv)
    wd = CardAddWindow(None, db)
    wd.show()
    sys.excepthook = lambda cls, exception, traceback: sys.__excepthook__(cls, exception, traceback)
    sys.exit(app.exec())