import hou
import json
from logging import getLogger
from abc import ABCMeta, abstractmethod
from typing import Union, Callable

logger = getLogger(__name__)
logger.setLevel(10)


def pretty_print_dict(d, indent=0):
    """
    Recursively pretty-prints nested dictionaries with indentation.

    Args:
        d (dict): The dictionary to pretty-print.
        indent (int): The current indentation level.

    Returns:
        str: The pretty-printed string.
    """
    lines = []
    for key, value in d.items():
        line = "  " * indent + str(key) + ":"
        if isinstance(value, dict):
            lines.append(line)
            lines.append(pretty_print_dict(value, indent + 1))
        elif isinstance(value, str) and value.startswith("{") and value.endswith("}"):
            lines.append(line)
            try:
                nested_dict = json.loads(value)
                lines.append(pretty_print_dict(nested_dict, indent + 1))
            except json.JSONDecodeError:
                lines.append("  " * (indent + 1) + value)
        else:
            lines.append(f"{line} {value}")
    return "\n".join(lines)


def node_validator(value, raise_error=False) -> hou.Node or None:
    """Validate node input. Accepts hou.Node, str, NodePropsMixin.
    Extracts node from wrappers, strings.
    If node is not valid, returns None.
    NOTE: NodePropsMixin must have a __call__ method.

    Args:
        value (hou.Node, str, NodePropsMixin): Node to validate
        raise_error (bool, optional): Whether to raise an error if node is not valid. Defaults to False.

    Returns:
        hou.Node: Validated node
        None: If node is not valid

    Raises:
        TypeError: If node is not valid"""

    if isinstance(value, hou.Node):
        logger.info(f"Node {value} is a hou.Node")
        return value
    elif isinstance(value, str):
        logger.info(f"Node {value} is a string")
        return hou.node(value)
    else:
        logger.warning(f"Node {value} is not valid")
        if raise_error:
            raise TypeError(f"Node {value} is not valid")
        return None


def get_ramp_values(
    node, parm_name
) -> tuple[list[Union[hou.rampBasis, str]], list[float], list[float]]:
    ramp_eval = node.parm(parm_name).eval()
    basis = list(ramp_eval.basis())
    keys = list(ramp_eval.keys())
    values = list(ramp_eval.values())
    return basis, keys, values


multiparm_types = [
    hou.folderType.MultiparmBlock,
    hou.folderType.ScrollingMultiparmBlock,
    hou.folderType.TabbedMultiparmBlock,
]


class ParmFilter(metaclass=ABCMeta):
    @abstractmethod
    def filter(self, parm_template):
        """Filter a parameter template.

        Args:
            parm_template (hou.ParmTemplate): The parameter template to filter.

        Returns:
            bool: Whether the parameter template is accepted or not.
        """
        raise NotImplementedError("This method must be implemented by a subclass")


class RampParmFilter(ParmFilter):
    def filter(self, parm_template) -> bool:
        return parm_template.type() == hou.parmTemplateType.Ramp


class AllParmFilter(ParmFilter):
    def filter(self, parm_template) -> bool:
        return True


class FloatParmFilter(ParmFilter):
    def filter(self, parm_template) -> bool:
        return parm_template.type() == hou.parmTemplateType.Float


class ParmInfo:
    """Get information about a Houdini node's parameters."""

    def __init__(self, node, parm_filter=None):
        # Validate node
        self.node = node_validator(node, raise_error=True)

        # Set the parm filter
        self.parm_filter = parm_filter if parm_filter else AllParmFilter()

        # Get node parm template group
        self.parm_template_group = self.node.parmTemplateGroup()

        # Get parameter naming scheme
        self.parm_naming_scheme = self.get_multiparm_naming_scheme()

    def parm_traverse(
        self, callback: Callable, group_or_folder=None, include_hidden=True
    ):
        """Traverse a group or folder and apply a callback function to each parm_template.

        Args:
            callback (Callable): Function to apply to each parm_template.
            group_or_folder (hou.ParmTemplateGroup or hou.FolderParmTemplate, optional): The group or folder to traverse.
            include_hidden (bool, optional): Whether to include hidden parameters.

        Returns:
            None
        """
        if group_or_folder is None:
            group_or_folder = (
                self.parm_template_group
            )  # You'll have to pass `self` in some way or define this function as a method.

        for parm_template in group_or_folder.parmTemplates():
            if parm_template.type() == hou.parmTemplateType.Separator:
                continue
            if not include_hidden and parm_template.isHidden():
                continue
            if parm_template.type() == hou.parmTemplateType.Folder:
                self.parm_traverse(callback, parm_template, include_hidden)
            else:
                callback(parm_template)

    def get_parm_names_cb(self, parm_template):
        """Callback function to get parm names"""
        if self.parm_filter.filter(parm_template):
            parm_names.add(parm_template.name())

    def get_parm_names(self, group_or_folder=None, include_hidden=True):
        """Wrapper for the parm_traverse, focused on getting parm names."""
        global parm_names
        parm_names = set()
        self.parm_traverse(self.get_parm_names_cb, group_or_folder, include_hidden)
        return list(parm_names)

    def get_parm_callbacks_cb(self, parm_template):
        """Callback function to get parm callbacks"""
        if self.parm_filter.filter(parm_template):
            parm_name = parm_template.name()
            callback_script = parm_template.scriptCallback()
            callback_language = parm_template.scriptCallbackLanguage()
            if callback_script:
                parm_callbacks[parm_name] = (callback_script, callback_language)

    def get_parm_callbacks(self, group_or_folder=None, include_hidden=True):
        """Wrapper for the parm_traverse, focused on getting parm callbacks."""
        global parm_callbacks
        parm_callbacks = {}
        self.parm_traverse(self.get_parm_callbacks_cb, group_or_folder, include_hidden)
        return parm_callbacks

    def get_parm_expressions_cb(self, parm_template):
        """Callback function to get parm expressions"""
        if self.parm_filter.filter(parm_template):
            parm_name = parm_template.name()
            if self.node.parm(parm_name) is None:
                return

            try:
                parm_expression = self.node.parm(parm_name).expression()
            except hou.OperationFailed:
                return
            if parm_expression:
                parm_expressions[parm_name] = parm_expression

    def get_parm_expressions(self, group_or_folder=None, include_hidden=True):
        """Wrapper for the parm_traverse, focused on getting parm expressions."""
        global parm_expressions
        parm_expressions = {}
        self.parm_traverse(
            self.get_parm_expressions_cb, group_or_folder, include_hidden
        )
        return parm_expressions

    def get_multiparm_naming_scheme(self) -> dict:
        """
        Returns names of the parameters in the multiparm template. Without index and # symbol.
        The key of the dictionary is the name of the multiparm block.
        The value is a list of strings, each representing the name of
        a parameter in the multiparm template.

        Args:
            node (hou.Node): The node that contains the multiparm template.

        Returns:
            dict: A dictionary where the keys are the names of the multiparm blocks
            and the values are lists of strings, each representing the name
            of a parameter in the multiparm template.
        """

        naming_schemes = {}
        for parm_template in self.parm_template_group.parmTemplates():
            # Ignore separators
            if parm_template.type() == hou.parmTemplateType.Separator:
                continue
            if parm_template.type() == hou.parmTemplateType.Folder:
                folder_type = parm_template.folderType()
                if folder_type in multiparm_types:
                    sub_parm_names = self.get_parm_names(parm_template)
                    sub_parm_names = [name.replace("#", "") for name in sub_parm_names]
                    naming_schemes[parm_template.name()] = sub_parm_names
        return naming_schemes
