from .utils import ParmInfo, pretty_print_dict
import hou


def get_parms_with_expressions(parm_info_instance) -> dict:
    """
    Get all parameters that have expressions in a node using the ParmInfo instance.

    Args:
        parm_info_instance (ParmInfo): An instance of the ParmInfo class.

    Returns:
        dict: A dictionary where keys are parameter names and values are expressions.
    """
    parm_expr_dict = {}
    parm_names = parm_info_instance.get_parm_names()
    node = parm_info_instance.node

    for parm_name in parm_names:
        parm = node.parm(parm_name)
        if parm:
            try:
                expression = parm.expression()
                if expression:
                    parm_expr_dict[parm_name] = expression
            except hou.OperationFailed:
                continue

    return parm_expr_dict


def get_parm_expressions_string(node):
    parm_info = ParmInfo(node)
    return pretty_print_dict(get_parms_with_expressions(parm_info), indent=1)
