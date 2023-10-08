from PySide2.QtWidgets import QTextEdit, QWidget, QVBoxLayout
from PySide2.QtGui import QTextOption
from .python_highlighter import PythonHighlighter
from .widgets_construct import NeatWidgetConstructor, NeatLayoutTypes


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
        self.main_widget.add_widget(self.edit_text_widget)
        self.layout.addWidget(self.main_widget)
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

    def __getattr__(self, name):
        """Delegate attribute access to the inner QTextEdit."""
        return getattr(self.edit_text_widget, name)