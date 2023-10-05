import hou


def traverse_parms_from_node(node, indent=0):
    """
    Traverse parameter templates from a given Houdini node.

    Args:
        node (hou.Node): Houdini node.
        indent (int): Current indentation level.

    Returns:
        str: Indented string representation of the parameter templates.
    """
    parm_template_group = node.parmTemplateGroup()
    parms = parm_template_group.entries()
    return traverse_parms(parms, indent)


def traverse_parms(parms, indent=0):
    """
    Traverse Houdini parameter templates and generate an indented string representation.

    Args:
        parms (list): List of Houdini parameter templates to traverse.
        indent (int): Current indentation level.

    Returns:
        str: Indented string representation of the parameter templates.
    """
    output_str = ""
    for parm in parms:
        if isinstance(parm, hou.FolderParmTemplate):
            if parm.label().strip():
                output_str += "    " * indent + f"## {parm.label()}\n"
            output_str += traverse_parms(parm.parmTemplates(), indent + 1)
        else:
            if parm.label().strip():
                output_str += "    " * indent + f"### {parm.label()}\n"
    return output_str
