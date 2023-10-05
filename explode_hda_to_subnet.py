import hou


def explode_me(node):
    nodePos = node.position()
    newName = node.name()
    nodePath = node.path()
    nodePath = nodePath.split(node.name())[0]

    parmDict = {}
    for parm in node.parms():
        if parm.isVisible() == True:
            try:
                parm.expression()
                expr = parm.expression()
            except:
                expr = None
            dictItem = {parm.name(): {"value": parm.eval(), "expression": expr}}
            parmDict.update(dictItem)

    template_group = node.parmTemplateGroup()

    newNode = hou.node(nodePath).createNode("subnet", newName + "_Cracked")
    newNode.setParmTemplateGroup(template_group)
    newNode.setPosition(nodePos + hou.Vector2(1, 0))
    for parm in newNode.parms():
        name = parm.name()
        try:
            newNode.parm(name).set(parmDict[name]["value"])
            if parmDict[name]["expression"] != None:
                newNode.parm(name).setExpression(parmDict[name]["expression"])
        except:
            pass

    for input in node.inputs():
        try:
            newNode.setNextInput(input)
        except:
            pass

    for i, output in enumerate(node.outputConnections()):
        output.outputItem().setInput(output.inputIndex(), newNode, output.outputIndex())
    node.bypass(True)
    hou.copyNodesTo(node.children(), newNode)
    newNode.setDisplayFlag(True)
