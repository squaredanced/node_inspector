import hou


def explode_me(node):
    nodePos = node.position()
    newName = node.name()
    nodePath = node.path()
    nodePath = nodePath.split(node.name())[0]

    # Collect parameter values first
    parmDict = {}
    for parm in node.parms():
        if parm.isVisible():
            try:
                expr = parm.expression()
            except:
                expr = None
            parmDict[parm.name()] = {"value": parm.eval(), "expression": expr}

    # Create the new node
    newNode = hou.node(nodePath).createNode("subnet", newName + "_Cracked")
    newNode.setPosition(nodePos + hou.Vector2(1, 0))

    # Set the template group
    template_group = node.parmTemplateGroup()
    newNode.setParmTemplateGroup(template_group)

    # Copy child nodes
    hou.copyNodesTo(node.children(), newNode)

    # Set parameter values
    for name, pd in parmDict.items():
        try:
            newNode.parm(name).set(pd["value"])
            if pd["expression"] is not None:
                newNode.parm(name).setExpression(pd["expression"])
        except:
            continue

    # Set connections
    for input in node.inputs():
        newNode.setNextInput(input)
    for i, output in enumerate(node.outputConnections()):
        output.outputItem().setInput(output.inputIndex(), newNode, output.outputIndex())

    node.bypass(True)
    newNode.setDisplayFlag(True)
