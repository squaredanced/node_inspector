import hou
from functools import partial
from .constants import BG_COLOR
from .generate_wrapper import generate_properties
from .get_all_labels import traverse_parms_from_node
from .edit_widget import EditWidget
from .utils import pretty_print_dict, node_validator, ParmInfo
from .explode_hda_to_subnet import explode_me
from .widgets_construct import NeatWidgetConstructor, NeatLayoutTypes
from PySide2.QtWidgets import (
    QPushButton,
    QWidget,
    QTabWidget,
    QMainWindow,
    QSplitter,
    QHBoxLayout,
    QLabel,
)
from PySide2.QtCore import Qt
from PySide2.QtGui import (
    QDragEnterEvent,
    QDropEvent,
    QDragMoveEvent,
)

# from .generate_wrapper import generate_properties


def text_edit_handler(node, text_edit, text=""):
    text_edit.clear()
    text_edit.append(text)


def get_user_data(node, text_edit):
    node_data = node.userDataDict()
    text = pretty_print_dict(node_data)
    text_edit_handler(node, text_edit, text)


def get_labels(node, text_edit):
    text = traverse_parms_from_node(node)

    text_edit_handler(node, text_edit, text)


def get_all_defaults(node, text_edit):
    text = pretty_print_dict(ParmInfo(node).get_parm_default_values(), indent=1)
    text_edit_handler(node, text_edit, text)


def get_all_expressions(node, text_edit):
    text = pretty_print_dict(
        ParmInfo(node).get_parm_expressions(include_hidden=True), indent=1
    )
    text_edit_handler(node, text_edit, text)


def get_all_conditionals(node, text_edit):
    text = pretty_print_dict(
        ParmInfo(node).get_parm_conditionals(include_hidden=True), indent=1
    )
    text_edit_handler(node, text_edit, text)


def generate_wrapper(node, text_edit):
    text = generate_properties(node)
    text_edit_handler(node, text_edit, text)


def explode_to_subnetwork(node, text_edit):
    explode_me(node)
    text_edit_handler(
        node, text_edit, text=f"Exploded node:\n\t{node.path()}\nto Subnetwork"
    )


def get_all_callbacks(node, text_edit):
    text = pretty_print_dict(ParmInfo(node).get_parm_callbacks(), indent=1)
    text_edit_handler(node, text_edit, text)


# Create a mapping between button names and functions
BUTTON_MAPPING = {
    "Get User Data": get_user_data,
    "Get Labels": get_labels,
    "Get All Defaults": get_all_defaults,
    "Get All Expressions": get_all_expressions,
    "Get All Callbacks": get_all_callbacks,
    "Get All Conditionals": get_all_conditionals,
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
            "QPushButton {background-color: rgb(10,10,10);"
            "color: rgb(200,200,200); border-radius: 10px; padding: 20px; margin: 5px;}"
            "QPushButton:hover {background-color: rgb(65,85,130);}"
            "QPushButton:checked {background-color: rgb(80,95,180);}"
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
    def __init__(self, parent=None, main_window=None):
        super(NodePathField, self).__init__(parent)
        self.setAcceptDrops(True)
        self.nodes = []
        self.main_window = main_window
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel("Drop Node Here")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(
            f"background-color: rgb(40,40,40); color: rgb(200,200,200);"
            + f"border-radius: 10px; margin: {MARGIN}px; padding: {PADDING}px;"
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
            node_data = event.mimeData().text()
            self.label.setText(node_data)
            for path in node_data.split(" "):
                self.nodes.append(node_validator(path))
            self.main_window.create_tabs()

            event.acceptProposedAction()


class MainWIndow(QMainWindow):
    def __init__(self, parent=hou.ui.mainQtWindow()):
        QMainWindow.__init__(self, parent, Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Node Inspector Tools")
        self.resize(1000, 200)

        self.central_widget = NeatWidgetConstructor(
            self,
            layout_type=NeatLayoutTypes.VERTICAL,
            enable_bg=True,
            background_color=BG_COLOR,
        )

        self.setCentralWidget(self.central_widget)
        self.buttons_list = []

        splitter = QSplitter(Qt.Horizontal)

        buttons_widget = NeatWidgetConstructor(
            self, layout_type=NeatLayoutTypes.VERTICAL, add_stretch=True
        )

        self.node_path_field = NodePathField(main_window=self)
        buttons_widget.add_widget(self.node_path_field)

        self.tabs = QTabWidget()

        self.node_edit_widgets = {}

        populate_buttons(
            sample_list=[i for i in BUTTON_MAPPING.keys()],
            buttons_list=self.buttons_list,
            layout=buttons_widget.main_layout,
            callback=self.button_callback,
            checkable=True,
            initial_checked=-1,
        )

        splitter.addWidget(buttons_widget)

        splitter.addWidget(buttons_widget)

        self.tabs.currentChanged.connect(self.on_tab_changed)
        splitter.addWidget(self.tabs)

        splitter.setStretchFactor(0, 0)  # buttons_widget, static
        splitter.setStretchFactor(1, 1)  # self.edit_text_widget, stretches

        self.central_widget.main_layout.addWidget(splitter)

    def create_edit_text(self):
        """Draft of the text edit widget, don't take it too seriously yet"""
        self.edit_text_widget = EditWidget()

    def button_callback(self, button_name):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.clear()
            node_name = self.tabs.tabText(self.tabs.currentIndex())
            node = hou.node(node_name)
            BUTTON_MAPPING[button_name](node, current_tab)

    def add_node(self, node_path):
        if node_path not in self.node_edit_widgets:
            node = hou.node(node_path)
            if node:
                edit_widget = EditWidget()
                self.tabs.addTab(edit_widget, node_path)
                self.node_edit_widgets[node_path] = edit_widget

    def on_tab_changed(self, index):
        """Triggered when tab is changed.

        Args:
            index (int): The index of the new tab.
        """
        # Find the currently checked button
        checked_button = None
        for button in self.buttons_list:
            if button.isChecked():
                checked_button = button.text()
                break

        # Exit if no button is checked
        if checked_button is None:
            return

        # Get the function mapped to the button and execute it
        button_name = button.text()
        if button_name in BUTTON_MAPPING:
            current_tab = self.tabs.currentWidget()
            if current_tab:
                current_tab.clear()
                node_name = self.tabs.tabText(self.tabs.currentIndex())
                node = hou.node(node_name)
                BUTTON_MAPPING[button_name](node, current_tab)

    def create_tabs(self):
        for node in self.node_path_field.nodes:
            self.add_node(node.path())
