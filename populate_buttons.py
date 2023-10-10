from functools import partial
from PySide2.QtWidgets import QPushButton


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
