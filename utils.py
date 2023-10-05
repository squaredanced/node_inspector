import hou
import json


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


def node_validator(path):
    if path:
        node = hou.node(path)
        if node:
            print("Valid Node Path Found", node)
            return node

        else:
            print("Non Valid Node Path")
            return None
