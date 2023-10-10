import hou
from .constants import BG_COLOR

from .edit_widget import EditWidget
from .populate_buttons import populate_buttons
from .utils import node_validator
from .button_callback_manager import BUTTON_MAPPING

from .widgets_construct import NeatWidgetConstructor, NeatLayoutTypes
from . import style
from PySide2.QtWidgets import (
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


MARGIN = 5
PADDING = 15


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

        # Add tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setStyleSheet(style.tab_style)

        self.node_edit_widgets = {}

        # Add buttons
        populate_buttons(
            sample_list=[i for i in BUTTON_MAPPING.keys()],
            buttons_list=self.buttons_list,
            layout=buttons_widget.main_layout,
            callback=self.button_callback,
            checkable=True,
            initial_checked=-1,
        )

        # Add buttons to layout
        splitter.addWidget(buttons_widget)

        # Connect tabs changed signal
        self.tabs.currentChanged.connect(self.on_tab_changed)

        splitter.addWidget(self.tabs)
        splitter.setStretchFactor(0, 0)  # buttons_widget, static
        splitter.setStretchFactor(1, 1)  # self.edit_text_widget, stretches

        # Set the splitter as the central widget
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
