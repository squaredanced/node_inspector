import hou
from functools import partial
import typing
from PySide2.QtWidgets import (
    QPushButton,
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QSplitter,
    QTextEdit,
    QGridLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QLabel,
)
from PySide2.QtCore import Qt, Slot
from PySide2.QtGui import (
    QTextOption,
    QDragEnterEvent,
    QDropEvent,
    QDragMoveEvent,
)
from enum import Enum


# Define your functions here
def get_user_data():
    print("Getting user data...")


def get_labels():
    print("Getting labels...")


def get_all_defaults():
    print("Getting all defaults...")


def get_all_expressions():
    print("Getting all expressions...")


def generate_wrapper():
    print("Generating wrapper...")


def explode_to_subnetwork():
    print("Exploding to subnetwork...")


# Create a mapping between button names and functions
BUTTON_MAPPING = {
    "Get User Data": get_user_data,
    "Get Labels": get_labels,
    "Get All Defaults": get_all_defaults,
    "Get All Expressions": get_all_expressions,
    "Generate Wrapper": generate_wrapper,
    "Explode To Subnetwork": explode_to_subnetwork,
}

MARGIN = 5
PADDING = 15


def populate_buttons(
    sample_list,
    buttons_list,
    layout,
    callback,
    checkable=False,
    width=30,
    fixed_width=False,
    uncheck=True,
    initial_checked=1,
    margin=5,
    padding=15,
):
    """Populate a layout with checkable buttons from list.
    Connects each button to a callback function.
    Pass the button value to the callback function.

    Args:
        sample_list (list): list of values to be used as button names
        buttons_list (list): list of buttons to be populated
        layout (QLayout): layout to be populated
        callback (function): function to be called on button press
        checkable (bool, optional): whether the button is checkable. Defaults to True.
        width (int, optional): width of the button. Defaults to 30.
        fixed_width (bool, optional): whether the button width is fixed. Defaults to True.
        uncheck (bool, optional): whether to uncheck other buttons when one is pressed. Defaults to True.

    Raises:
        TypeError: if buttons_list is not a list
        Warning: if sample_list is None or empty
        TypeError: if sample_list is not a list

    """

    def set_unchecked(button, buttons):
        """Set all buttons in a list to unchecked, except the one that was pressed

        Args:
            button (QPushButton): button that was pressed
            buttons (list): list of buttons to be unchecked
        """
        for b in buttons:
            if b != button:
                b.setChecked(False)

    # properly handle mutable default arguments
    # raise an error if buttons_list is not list
    if buttons_list is None:
        buttons_list = []

    if not isinstance(buttons_list, list):
        raise TypeError("buttons_list must be a list")

    # handle sample_list being None or empty
    if sample_list is None or len(sample_list) == 0:
        # raise warning if sample_list is None or empty
        raise Warning("sample_list is None or empty")

    # raise error if sample_list is not list
    if not isinstance(sample_list, list):
        raise TypeError("sample_list must be a list")

    for n, i in enumerate(sample_list):
        button = QPushButton(" ".join(str(i).split("_")).title())
        button.setStyleSheet(
            "QPushButton {background-color: rgb(50,50,50); color: rgb(200,200,200); border-radius: 10px; padding: 20px; margin: 5px;}"
            "QPushButton:hover {background-color: rgb(60,60,60);}"
            "QPushButton:checked {background-color: rgb(70,70,70);}"
            "QPushButton:pressed {background-color: rgb(80,80,80);}"
        )
        if checkable:
            button.setCheckable(True)
        if n == initial_checked and checkable:
            button.setChecked(True)
        if fixed_width:
            button.setFixedWidth(width)
        buttons_list.append(button)
        button.pressed.connect(partial(callback, i))
        layout.addWidget(button)

    # If button is pressed, set all other buttons to unchecked
    if uncheck:
        for button in buttons_list:
            button.pressed.connect(
                lambda button=button: set_unchecked(button, buttons_list)
            )


def node_validator(path):
    if path:
        node = hou.node(path)
        if node:
            print("Valid Node Path Found", node)
            return node

        else:
            print("Non Valid Node Path")
            return None


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


class NodePathField(QWidget):
    def __init__(self, parent=None):
        super(NodePathField, self).__init__(parent)
        self.setAcceptDrops(True)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel("Drop Node Here")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(
            f"background-color: rgb(40,40,40); color: rgb(200,200,200); border-radius: 10px; margin: {MARGIN}px; padding: {PADDING}px;"
        )
        self.main_layout.addWidget(self.label)
        self.setLayout(self.main_layout)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasText():
            self.label.setText(event.mimeData().text())
            node_validator(event.mimeData().text())

            event.acceptProposedAction()


class MainWIndow(QMainWindow):
    def __init__(self, parent=hou.ui.mainQtWindow()):
        QMainWindow.__init__(self, parent, Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Node Inspector Tools")
        self.resize(400, 200)
        self.central_widget = NeatWidgetConstructor(
            self, layout_type=NeatLayoutTypes.VERTICAL
        )
        self.setCentralWidget(self.central_widget)

        splitter = QSplitter(Qt.Horizontal)
        buttons_widget = NeatWidgetConstructor(
            self, layout_type=NeatLayoutTypes.VERTICAL, add_stretch=True
        )

        node_path_field = NodePathField()
        buttons_widget.add_widget(node_path_field)

        populate_buttons(
            sample_list=[i for i in BUTTON_MAPPING.keys()],
            buttons_list=[],
            layout=buttons_widget.main_layout,
            callback=self.button_callback,
        )

        splitter.addWidget(buttons_widget)

        # Add QTextEdit Widget with synatax set to python

        self.create_edit_text()
        splitter.addWidget(self.edit_text_widget)
        self.central_widget.main_layout.addWidget(splitter)

    def create_edit_text(self):
        self.edit_text_widget = QTextEdit()
        self.edit_text_widget.setReadOnly(True)
        self.edit_text_widget.setLineWrapMode(QTextEdit.NoWrap)
        self.edit_text_widget.setTabStopWidth(20)
        self.edit_text_widget.setFontFamily("Courier")
        self.edit_text_widget.setFontPointSize(10)
        self.edit_text_widget.setLineWrapMode(QTextEdit.FixedPixelWidth)
        self.edit_text_widget.setLineWrapColumnOrWidth(600)
        self.edit_text_widget.setWordWrapMode(QTextOption.NoWrap)
        self.edit_text_widget.setStyleSheet(
            "background-color: rgb(40,40,40); color: rgb(200,200,200);"
        )
        return self.edit_text_widget

    def button_callback(self, button_name):
        self.edit_text_widget.clear()
        self.edit_text_widget.append(button_name)
        BUTTON_MAPPING[button_name]()
