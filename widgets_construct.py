from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFormLayout,
    QPushButton,
)

from PySide2.QtCore import Qt, Slot
from enum import Enum


class NeatLayoutTypes(Enum):
    VERTICAL = QVBoxLayout
    HORIZONTAL = QHBoxLayout
    GRID = QGridLayout
    FORM = QFormLayout


class NeatWidgetConstructor(QWidget):
    def __init__(
        self,
        parent=None,
        layout_type=NeatLayoutTypes.VERTICAL,
        enable_bg=False,
        add_stretch=False,
        margin=10,
        background_color="rgba(5,6,7,255)",
    ):
        super().__init__(parent)

        self.main_layout = layout_type.value(self)
        self.setLayout(self.main_layout)
        self.enable_bg = enable_bg
        if self.enable_bg:
            self.setAttribute(Qt.WA_StyledBackground, True)
            self.setStyleSheet(f"background-color: {background_color} ;")
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(margin, margin, margin, margin)

        self.add_stretch = add_stretch
        self.stretch_added = False

    def add_widget(self, widget, stretch=0):
        # Simply add a widget to the layout
        self.main_layout.addWidget(widget, stretch)

    def showEvent(self, event):
        # When the widget is shown, add a stretch to the layout
        if not self.stretch_added and self.add_stretch:
            self.main_layout.addStretch(1)
            self.stretch_added = True
        super().showEvent(event)


class NeatWidgetConstructorCollapsible(QWidget):
    def __init__(
        self,
        parent=None,
        layout_type=NeatLayoutTypes.VERTICAL,
        enable_bg=False,
        add_stretch=False,
        margin=10,
        background_color="rgba(5,6,7,80)",
    ):
        """A widget that can be collapsed and expanded.
        Designed for being container for widgets. Can be collapsed and expanded"""

        super().__init__(parent)

        self.visibility_states = {}
        self.main_layout = layout_type.value(self)
        self.setLayout(self.main_layout)
        self.enable_bg = enable_bg
        self.collapsed = False
        self.button = QPushButton()
        self.button.setMaximumSize(15, 15)
        self.button.setStyleSheet(
            "border-radius: 7px; background-color: white;"
        )  # Making it a round button

        if self.enable_bg:
            self.setAttribute(Qt.WA_StyledBackground, True)
            self.setStyleSheet(f"background-color:{background_color};")

        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(margin, margin, margin, margin)

        self.button.clicked.connect(
            self.toggle_collapse
        )  # Connecting button click to toggle method

        self.add_stretch = add_stretch
        self.stretch_added = False

        self.main_layout.addWidget(self.button)  # Add the round button to the layout

    @Slot()
    def toggle_collapse(self):
        self.collapsed = not self.collapsed

        if self.collapsed:
            self.button.setStyleSheet("border-radius: 7px; background-color: red;")
        else:
            self.button.setStyleSheet("border-radius: 7px; background-color: white;")

        self.apply_visibility()

    def apply_visibility(self):
        for i in range(1, self.main_layout.count()):
            item = self.main_layout.itemAt(i)
            if hasattr(item, "widget") and item.widget():
                widget = item.widget()
                if self.collapsed:
                    self.visibility_states[widget] = widget.isVisible()
                    widget.hide()
                else:
                    widget.setVisible(self.visibility_states.get(widget, True))

    def add_widget(self, widget, stretch=0):
        self.main_layout.addWidget(widget, stretch)
        self.visibility_states[widget] = widget.isVisible()

    def showEvent(self, event):
        if not self.stretch_added and self.add_stretch:
            self.main_layout.addStretch(1)
            self.stretch_added = True
        super().showEvent(event)
