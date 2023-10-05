import hou

print("Also imported from a folder!")


def generate_properties(node):
    """
    Generate Python property and setter methods for a given hou.Node's parameters.

    Args:
        node (hou.Node): The Houdini node for which to generate the properties.

    Returns:
        str: The string containing the Python property and setter methods.
    """
    # Initialize an empty string to store the resulting code
    output_code = ""

    # Loop through all parameter templates
    for parm_template in node.parmTemplateGroup().entries():
        # Skip folders and separators
        if isinstance(parm_template, hou.FolderParmTemplate) or isinstance(
            parm_template, hou.SeparatorParmTemplate
        ):
            continue

        # Extract the name of the parameter
        parm_name = parm_template.name()

        # Generate the @property code
        property_code = f"""
    @property
    def {parm_name}(self):
        return self.node.parm("{parm_name}").eval()
"""

        # Generate the @setter code
        setter_code = f"""
    @{parm_name}.setter
    def {parm_name}(self, value):
        self.node.parm("{parm_name}").set(value)
"""
        # Concatenate the generated code
        output_code += property_code + setter_code

    return output_code
