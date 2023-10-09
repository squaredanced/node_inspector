from PySide2.QtWidgets import QTextEdit, QWidget, QVBoxLayout, QPushButton
from PySide2.QtGui import QTextOption
from .python_highlighter import PythonHighlighter
from .widgets_construct import NeatWidgetConstructor, NeatLayoutTypes
from .constants import BG_COLOR


class EditWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.edit_text_widget = None
        self.syntax_highlighter = None

        self.main_widget = NeatWidgetConstructor(
            layout_type=NeatLayoutTypes.VERTICAL, enable_bg=True
        )

        self.edit_text_widget = QTextEdit()
        self.setup_text_edit()
        self.main_widget.add_widget(self.edit_text_widget, stretch=1)
        self.layout.addWidget(self.main_widget)
        self.add_text_size_controls()
        self.setLayout(self.layout)

        self.syntax_highlighter = PythonHighlighter(self.edit_text_widget.document())

    def setup_text_edit(self):
        self.edit_text_widget.setReadOnly(True)
        self.edit_text_widget.setLineWrapMode(QTextEdit.NoWrap)
        self.edit_text_widget.setTabStopWidth(20)
        self.edit_text_widget.setFontFamily("Courier")
        self.edit_text_widget.setFontPointSize(15)
        self.edit_text_widget.setLineWrapMode(QTextEdit.FixedPixelWidth)
        self.edit_text_widget.setLineWrapColumnOrWidth(600)
        self.edit_text_widget.setWordWrapMode(QTextOption.NoWrap)
        self.edit_text_widget.setStyleSheet("background-color: rgb(5,5,5);")

    def add_text_size_controls(self):
        self.buttons_holder = NeatWidgetConstructor(
            layout_type=NeatLayoutTypes.HORIZONTAL,
            add_stretch=True,
            enable_bg=True,
            background_color=BG_COLOR,
        )
        self.buttons_holder.add_widget(
            self.create_button(" + ", self.increase_font_size)
        )
        self.buttons_holder.add_widget(
            self.create_button(" - ", self.decrease_font_size)
        )
        self.main_widget.add_widget(self.buttons_holder, stretch=0)

    def create_button(self, text, callback):
        button = QPushButton(text)
        font = button.font()
        font.setPointSize(12)
        font.setBold(True)
        button.setFont(font)
        button.setStyleSheet(
            f"QPushButton {{background-color: rgb(5,7,12); color: rgb(200,200,200); border-radius: 10px; padding: 10px; margin: 2px;}}"
            + f"QPushButton:hover {{background-color: rgb(65,85,130);}}"
            + f"QPushButton:checked {{background-color: rgb(70,70,70);}}"
            + f"QPushButton:pressed {{background-color: rgb(80,95,180);}}"
        )
        button.clicked.connect(callback)
        return button

    def refresh_highlighting(self):
        cursor_position = self.edit_text_widget.textCursor().position()
        content = self.edit_text_widget.toPlainText()
        self.edit_text_widget.setPlainText("")  # Clear text
        self.edit_text_widget.setPlainText(content)  # Reset text
        cursor = self.edit_text_widget.textCursor()
        cursor.setPosition(cursor_position)
        self.edit_text_widget.setTextCursor(cursor)

    def increase_font_size(self):
        font_size = self.edit_text_widget.fontPointSize()
        self.edit_text_widget.setFontPointSize(font_size + 1)
        self.refresh_highlighting()

    def decrease_font_size(self):
        font_size = self.edit_text_widget.fontPointSize()
        self.edit_text_widget.setFontPointSize(font_size - 1)
        self.refresh_highlighting()

    def __getattr__(self, name):
        """Delegate attribute access to the inner QTextEdit."""
        return getattr(self.edit_text_widget, name)
