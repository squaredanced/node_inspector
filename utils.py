import hou
import json
from logging import getLogger
from abc import ABCMeta, abstractmethod
from typing import Union

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

    def get_parm_names(self, group_or_folder=None, include_hidden=True) -> list:
        """Get all parameter names from a group or folder.

        Args:
            group_or_folder (hou.ParmTemplateGroup or hou.FolderParmTemplate):
                The group or folder to get the parameter names from.
                if None, the node's parmTemplateGroup is used. Defaults to None.

            include_hidden (bool, optional): Whether to include hidden parameters. Defaults to True.

        Returns:
            list: A list of parameter names.
        """

        if group_or_folder is None:
            group_or_folder = self.parm_template_group

        parm_names = set()
        for parm_template in group_or_folder.parmTemplates():
            if parm_template.type() == hou.parmTemplateType.Separator:
                continue
            if not include_hidden and parm_template.isHidden():
                continue
            if parm_template.type() == hou.parmTemplateType.Folder:
                sub_parm_names = self.get_parm_names(parm_template, include_hidden)
                parm_names.update(sub_parm_names)
            elif self.parm_filter.filter(parm_template):
                parm_names.add(parm_template.name())
        return list(parm_names)

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
