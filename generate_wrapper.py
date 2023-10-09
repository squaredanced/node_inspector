import hou


def generate_properties(node):
    class_name = "".join(word.title() for word in node.name().split("_"))
    code = f"class {class_name}Wrapper:\n    def __init__(self, node):\n        self.node = node\n"

    parm_template_group = node.parmTemplateGroup()
    folder_parms = {}

    for parm_template in parm_template_group.entries():
        if isinstance(parm_template, hou.FolderParmTemplate):
            folder_name = parm_template.name()
            folder_parms[folder_name] = parm_template.parmTemplates()
        else:
            folder_parms["root"] = folder_parms.get("root", [])
            folder_parms["root"].append(parm_template)

    for folder, parms in folder_parms.items():
        if folder != "root":
            code += f"    # from folder {folder}\n"

        for parm_template in parms:
            if isinstance(
                parm_template, (hou.SeparatorParmTemplate, hou.FolderParmTemplate)
            ):
                continue

            parm_name = parm_template.name()
            code += f"""
    @property
    def {parm_name}(self):
        return self.node.parm('{parm_name}').eval()

    @{parm_name}.setter
    def {parm_name}(self, value):
        self.node.parm('{parm_name}').set(value)
"""
    return code


def generate_properties_for_folder(folder_parm_template, indent):
    """
    Generate Python property and setter methods for folder parameter templates.

    Args:
        folder_parm_template (hou.FolderParmTemplate): The folder parameter template.
        indent (int): Current indentation level.

    Returns:
        str: The string containing the Python property and setter methods.
    """
    output_code = ""
    for parm_template in folder_parm_template.parmTemplates():
        if isinstance(parm_template, hou.FolderParmTemplate):
            output_code += generate_properties_for_folder(parm_template, indent + 1)
        else:
            parm_name = parm_template.name()
            property_code = f"""
    @property
    def {parm_name}(self):
        return self.node.parm("{parm_name}").eval()
"""

            setter_code = f"""
    @{parm_name}.setter
    def {parm_name}(self, value):
        self.node.parm("{parm_name}").set(value)
"""

            output_code += property_code + setter_code

    return output_code
