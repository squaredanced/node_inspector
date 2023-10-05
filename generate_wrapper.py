import hou

print("Also imported from a folder!")


def generate_properties(node, indent=0):
    """
    Generate Python property and setter methods for a given hou.Node's parameters.

    Args:
        node (hou.Node): The Houdini node for which to generate the properties.
        indent (int): Current indentation level.

    Returns:
        str: The string containing the Python property and setter methods.
    """
    output_code = ""
    parm_template_group = node.parmTemplateGroup()
    parms = parm_template_group.entries()

    for parm_template in parms:
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
