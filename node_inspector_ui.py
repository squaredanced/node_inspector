import hou
from functools import partial
from .generate_wrapper import generate_properties
from .get_all_labels import traverse_parms_from_node
from .python_highlighter import PythonHighlighter
from .utils import pretty_print_dict
from .utils import node_validator
from .explode_hda_to_subnet import explode_me
from .widgets_construct import NeatWidgetConstructor, NeatLayoutTypes
from PySide2.QtWidgets import (
    QPushButton,
    QWidget,
    QMainWindow,
    QSplitter,
    QTextEdit,
    QHBoxLayout,
    QLabel,
)
from PySide2.QtCore import Qt
from PySide2.QtGui import (
    QTextOption,
    QDragEnterEvent,
    QDropEvent,
    QDragMoveEvent,
)
import json

# from .generate_wrapper import generate_properties


def text_edit_handler(node, text_edit, text=""):
    text_edit.clear()
    text_edit.append(text)


def get_user_data(node, text_edit):
    node_data = node.userDataDict()
    text = pretty_print_dict(node_data)
    text_edit_handler(node, text_edit, text)

    text = pretty_print_dict(node_data)
    text_edit_handler(node, text_edit, text)


def get_labels(node, text_edit):
    text = traverse_parms_from_node(node)

    text_edit_handler(node, text_edit, text)


def get_all_defaults(node, text_edit):
    print(f"Getting all defaults... {node}")
    text_edit_handler(node, text_edit)


def get_all_expressions(node, text_edit):
    print(f"Getting all expressions... {node}")
    text_edit_handler(node, text_edit)


def generate_wrapper(node, text_edit):
    text = generate_properties(node)
    text_edit_handler(node, text_edit, text)


def explode_to_subnetwork(node, text_edit):
    text = explode_me(node)
    text_edit_handler(
        node, text_edit, text=f"Exploded node:\n\t{node.path()}\nto Subnetwork"
    )


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
            "QPushButton {background-color: rgb(10,10,10); color: rgb(200,200,200); border-radius: 10px; padding: 20px; margin: 5px;}"
            "QPushButton:hover {background-color: rgb(65,85,130);}"
            "QPushButton:checked {background-color: rgb(70,70,70);}"
            "QPushButton:pressed {background-color: rgb(80,95,180);}"
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


class NodePathField(QWidget):
    def __init__(self, parent=None):
        super(NodePathField, self).__init__(parent)
        self.setAcceptDrops(True)
        self.node = None

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
            self.node = node_validator(event.mimeData().text())

            event.acceptProposedAction()


class MainWIndow(QMainWindow):
    def __init__(self, parent=hou.ui.mainQtWindow()):
        QMainWindow.__init__(self, parent, Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Node Inspector Tools")
        self.resize(800, 200)
        self.central_widget = NeatWidgetConstructor(
            self, layout_type=NeatLayoutTypes.VERTICAL
        )
        self.setCentralWidget(self.central_widget)

        splitter = QSplitter(Qt.Horizontal)
        buttons_widget = NeatWidgetConstructor(
            self, layout_type=NeatLayoutTypes.VERTICAL, add_stretch=True
        )

        self.node_path_field = NodePathField()
        buttons_widget.add_widget(self.node_path_field)

        populate_buttons(
            sample_list=[i for i in BUTTON_MAPPING.keys()],
            buttons_list=[],
            layout=buttons_widget.main_layout,
            callback=self.button_callback,
        )

        splitter.addWidget(buttons_widget)

        # Add QTextEdit Widget with syntax set to python

        self.create_edit_text()
        splitter.addWidget(self.edit_text_widget)

        splitter.setStretchFactor(0, 0)  # buttons_widget, static
        splitter.setStretchFactor(1, 1)  # self.edit_text_widget, stretches

        self.central_widget.main_layout.addWidget(splitter)

    def create_edit_text(self):
        self.edit_text_widget = QTextEdit()
        self.edit_text_widget.setReadOnly(True)
        self.edit_text_widget.setLineWrapMode(QTextEdit.NoWrap)
        self.edit_text_widget.setTabStopWidth(20)
        self.edit_text_widget.setFontFamily("Courier")
        self.edit_text_widget.setFontPointSize(15)
        self.edit_text_widget.setLineWrapMode(QTextEdit.FixedPixelWidth)
        self.edit_text_widget.setLineWrapColumnOrWidth(600)
        self.edit_text_widget.setWordWrapMode(QTextOption.NoWrap)
        self.edit_text_widget.setStyleSheet("background-color: rgb(5,5,5);")
        self.syntax_highlighter = PythonHighlighter(self.edit_text_widget.document())
        return self.edit_text_widget

    def button_callback(self, button_name):
        self.edit_text_widget.clear()

        BUTTON_MAPPING[button_name](self.node_path_field.node, self.edit_text_widget)
