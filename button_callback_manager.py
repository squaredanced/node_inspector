from .utils import pretty_print_dict, ParmInfo
from .get_all_labels import traverse_parms_from_node
from .generate_wrapper import generate_properties
from .explode_hda_to_subnet import explode_me


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
