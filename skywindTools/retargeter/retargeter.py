import pymel.core as pmc
import pymel.core.datatypes as dt
import controltools
import logging

##############################
#      Private Methods       #
##############################

class _undoBlock(object):

    def __enter__(self):
        pmc.undoInfo(openChunk=True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pmc.undoInfo(closeChunk=True)
        if exc_val is not None:
            pmc.undo()

def _bind(source, target, translate, rotate, snapTranslation=True, snapRotation=True, scale=10.0):

    # Create the nodes
    tBuffer = pmc.group(empty=True, n=target.shortName() + '_NODE')
    _connectToTarget(tBuffer, target)
    _addToNodeGroup(tBuffer)

    tNode = _createNode(curveData=CUBE_CURVEDATA, scale=scale, color=dt.Color(1,1,0))
    pmc.rename(tNode, target.shortName() + '_translateOffset')
    pmc.parent(tNode, tBuffer)

    rBuffer = pmc.group(empty=True, n=target.shortName() + '_rotateBuffer')
    pmc.parent(rBuffer, tNode)

    rNode = _createNode(curveData=OCTO_CURVEDATA, scale=scale/2, color=dt.Color.blue)
    pmc.rename(rNode, target.shortName() + '_rotateOffset')
    pmc.parent(rNode, rBuffer)

    # Set the nodes default positions and reset them
    if snapTranslation:
        tBuffer.setTranslation(target.getTranslation(worldSpace=True), worldSpace=True)
    else:
        tBuffer.setTranslation(source.getTranslation(worldSpace=True), worldSpace=True)

    if snapRotation:
        rBuffer.setRotation(target.getRotation(worldSpace=True), worldSpace=True)
    else:
        rBuffer.setRotation(source.getRotation(worldSpace=True), worldSpace=True)

    if translate:
        pmc.pointConstraint(source, tBuffer, mo=True)

    if rotate:
        pmc.orientConstraint(source, rBuffer, mo=True)

        if not translate and target.getParent() is not None:
            pmc.parentConstraint(target.getParent(), tBuffer, mo=True)

    pmc.pointConstraint(tNode, target, mo=snapTranslation)
    pmc.orientConstraint(rNode, target, mo=snapRotation)

    # Lock and hide the controls we don't want modified
    pmc.setAttr(tNode.rotate, channelBox=False, keyable=False, lock=True)
    pmc.setAttr(rNode.translate, channelBox=False, keyable=False, lock=True)
    pmc.setAttr(tNode.scale, channelBox=False, keyable=False, lock=True)
    pmc.setAttr(rNode.scale, channelBox=False, keyable=False, lock=True)

def _connectToTarget(node, target):

    # Add message attributes to the node and its target
    if not pmc.hasAttr(node, 'bindTarget'):
        pmc.addAttr(node, ln='bindTarget', at='message')

    if not pmc.hasAttr(target, 'bindNode'):
        pmc.addAttr(target, ln='bindNode', at='message')

    # Connect the attributes
    pmc.connectAttr(node.bindTarget, target.bindNode, force=True)

def _findBindNodes():

    # Grab a list of every bind node in the scene
    return [obj for obj in pmc.ls(dag=True) if pmc.hasAttr(obj, 'bindTarget', checkShape=False)]

def _findBindTargets():

    # Grab all the bind nodes, and create a list of their targets
    return [pmc.getAttr(node.bindTarget) for node in _findBindNodes()]

def _createNode(curveData=None, scale=1.0, color=dt.Color(1,1,0)):

    # Create the node and set its base size
    node = controltools.create_control_curve_from_data(curveData)
    controltools.scale_curve(scale, scale, scale, node)
    pmc.makeIdentity(node, scale=True, apply=True)

    # Color the node
    for shape in node.getShapes():
        pmc.setAttr(shape.overrideColorRGB, color)
        pmc.setAttr(shape.overrideRGBColors, True)
        pmc.setAttr(shape.overrideEnabled, True)

    return node

def _removeNode(node):

    target = pmc.getAttr(node.bindTarget)
    pmc.deleteAttr(target.bindNode)
    pmc.deleteAttr(node.bindTarget)

    pmc.delete(node)

def _bake(targets):

    # Grab the start and end frame
    start = int(pmc.playbackOptions(ast=True, q=True))
    end = int(pmc.playbackOptions(aet=True, q=True))

    # Bake the targets
    pmc.bakeResults(targets, t=(start, end), hi='none', simulation=True)

    # Delete all the baked nodes
    for node in _findBindNodes():
        pmc.delete(node)

def _addToNodeGroup(node):

    if not pmc.objExists('BIND_NODES'):
        group = pmc.group(empty=True, n='BIND_NODES')

    pmc.parent(node, pmc.PyNode('BIND_NODES'))

##############################
#      Public Methods       #
##############################

def bakeBindTargets():

    # Grab a list of all targets
    targets = _findBindTargets()

    if len(targets) > 0:

        with _undoBlock():
            _bake(targets)

    else:
        logging.warning('No Bind Nodes in scene')

def selectBindNodes():

    nodes = _findBindNodes()

    if len(nodes) > 0:

        # First clear the selection
        pmc.select(clear=True)

        # Then select all bind nodes
        pmc.select(nodes)

    else:
        logging.warning('No bind nodes to select')

def removeSelectedNodes():

    nodes = [obj for obj in pmc.selected() if pmc.hasAttr(obj, 'bindTarget')]

    if len(nodes) > 0:
        for node in nodes:
            _removeNode(node)
    else:
        logging.warning('No valid nodes selected')

def selectBindTargets():

    targets = _findBindTargets()

    if len(targets) > 0:

        # First clear the selection
        pmc.select(clear=True)

        # Then select all bind targets
        pmc.select(targets)

    else:
        logging.warning('No targets to select')

def bindSelected(scale, translate, rotate, snapT, snapR):

    # Grab the selection
    selection = pmc.selected()

    if len(selection) > 1:

        # Grab the selections we care about
        source = selection[0]
        target = selection[1]

        # Bind the targets
        with _undoBlock():
            _bind(source, target, translate, rotate, snapTranslation=snapT, snapRotation=snapR, scale=scale)


    else:
        logging.warning('Not enough targets')

def buildIKChainSelected():

    def createScaledLocator(name='unnamed'):
        loc = pmc.spaceLocator(name)
        loc.localScaleX.set(20)
        loc.localScaleY.set(20)
        loc.localScaleZ.set(20)
        return loc

    with _undoBlock():
        targets = [obj for obj in pmc.selected() if isinstance(obj, pmc.nodetypes.Joint)]

        assert len(targets) >= 2, 'Not enough valid targets selected.'

        start_joint = targets[0]
        pole_joint = targets[0].getChildren()[0]
        end_joint = targets[1]

        handle = pmc.ikHandle(sj=start_joint, ee=end_joint)[0]

        ik_ctrl = createScaledLocator(name='ik_ctrl')
        ik_ctrl.setTranslation(end_joint.getTranslation(space='world'), space='world')
        pmc.orientConstraint(ik_ctrl, end_joint, mo=True)
        pmc.parent(handle, ik_ctrl)


        start_ctrl = createScaledLocator(name='start_ctrl')
        start_ctrl.setMatrix(start_joint.getMatrix(worldSpace=True), worldSpace=True)
        pmc.parentConstraint(start_ctrl, start_joint, mo=True)

        group = pmc.group(empty=True, name=targets[0].name() + '_IKGRP')
        pole_ctrl = createScaledLocator(name='pole_ctrl')
        pole_ctrl.setTranslation(pole_joint.getTranslation(space='world'), space='world')
        pmc.poleVectorConstraint(pole_ctrl, handle)

        pmc.parent([ik_ctrl, start_ctrl, pole_ctrl], group)


##### Shapes #####

SPHERE_CURVEDATA = [
        {
            "knots": [
                -2.0,
                -1.0,
                0.0,
                1.0,
                2.0,
                3.0,
                4.0,
                5.0,
                6.0,
                7.0,
                8.0,
                9.0,
                10.0
            ],
            "cvs": [
                [
                    0.783611624891225,
                    4.798237340988468e-17,
                    -0.7836116248912238
                ],
                [
                    -1.2643170607829326e-16,
                    6.785732323110913e-17,
                    -1.108194187554388
                ],
                [
                    -0.7836116248912243,
                    4.798237340988471e-17,
                    -0.7836116248912243
                ],
                [
                    -1.108194187554388,
                    1.966335461618786e-32,
                    -3.21126950723723e-16
                ],
                [
                    -0.7836116248912245,
                    -4.7982373409884694e-17,
                    0.783611624891224
                ],
                [
                    -3.3392053635905195e-16,
                    -6.785732323110915e-17,
                    1.1081941875543881
                ],
                [
                    0.7836116248912238,
                    -4.798237340988472e-17,
                    0.7836116248912244
                ],
                [
                    1.108194187554388,
                    -3.644630067904792e-32,
                    5.952132599280585e-16
                ],
                [
                    0.783611624891225,
                    4.798237340988468e-17,
                    -0.7836116248912238
                ],
                [
                    -1.2643170607829326e-16,
                    6.785732323110913e-17,
                    -1.108194187554388
                ],
                [
                    -0.7836116248912243,
                    4.798237340988471e-17,
                    -0.7836116248912243
                ]
            ],
            "degree": 3
        },
        {
            "knots": [
                -2.0,
                -1.0,
                0.0,
                1.0,
                2.0,
                3.0,
                4.0,
                5.0,
                6.0,
                7.0,
                8.0,
                9.0,
                10.0
            ],
            "cvs": [
                [
                    4.7982373409884756e-17,
                    0.7836116248912238,
                    -0.783611624891225
                ],
                [
                    -7.74170920797604e-33,
                    1.108194187554388,
                    1.2643170607829326e-16
                ],
                [
                    -4.798237340988471e-17,
                    0.7836116248912243,
                    0.7836116248912243
                ],
                [
                    -6.785732323110913e-17,
                    3.21126950723723e-16,
                    1.108194187554388
                ],
                [
                    -4.7982373409884725e-17,
                    -0.783611624891224,
                    0.7836116248912245
                ],
                [
                    -2.0446735801084019e-32,
                    -1.1081941875543881,
                    3.3392053635905195e-16
                ],
                [
                    4.798237340988468e-17,
                    -0.7836116248912244,
                    -0.7836116248912238
                ],
                [
                    6.785732323110913e-17,
                    -5.952132599280585e-16,
                    -1.108194187554388
                ],
                [
                    4.7982373409884756e-17,
                    0.7836116248912238,
                    -0.783611624891225
                ],
                [
                    -7.74170920797604e-33,
                    1.108194187554388,
                    1.2643170607829326e-16
                ],
                [
                    -4.798237340988471e-17,
                    0.7836116248912243,
                    0.7836116248912243
                ]
            ],
            "degree": 3
        },
        {
            "knots": [
                -2.0,
                -1.0,
                0.0,
                1.0,
                2.0,
                3.0,
                4.0,
                5.0,
                6.0,
                7.0,
                8.0,
                9.0,
                10.0
            ],
            "cvs": [
                [
                    0.783611624891225,
                    0.7836116248912238,
                    0.0
                ],
                [
                    -1.2643170607829326e-16,
                    1.108194187554388,
                    0.0
                ],
                [
                    -0.7836116248912243,
                    0.7836116248912243,
                    0.0
                ],
                [
                    -1.108194187554388,
                    3.21126950723723e-16,
                    0.0
                ],
                [
                    -0.7836116248912245,
                    -0.783611624891224,
                    0.0
                ],
                [
                    -3.3392053635905195e-16,
                    -1.1081941875543881,
                    0.0
                ],
                [
                    0.7836116248912238,
                    -0.7836116248912244,
                    0.0
                ],
                [
                    1.108194187554388,
                    -5.952132599280585e-16,
                    0.0
                ],
                [
                    0.783611624891225,
                    0.7836116248912238,
                    0.0
                ],
                [
                    -1.2643170607829326e-16,
                    1.108194187554388,
                    0.0
                ],
                [
                    -0.7836116248912243,
                    0.7836116248912243,
                    0.0
                ]
            ],
            "degree": 3
        }
    ]

CUBE_CURVEDATA = [
        {
            "knots": [
                0.0,
                1.0,
                2.0,
                3.0,
                4.0,
                5.0,
                6.0,
                7.0,
                8.0,
                9.0,
                10.0,
                11.0,
                12.0,
                13.0,
                14.0,
                15.0
            ],
            "cvs": [
                [
                    0.5,
                    0.5,
                    0.5
                ],
                [
                    0.5,
                    0.5,
                    -0.5
                ],
                [
                    -0.5,
                    0.5,
                    -0.5
                ],
                [
                    -0.5,
                    0.5,
                    0.5
                ],
                [
                    0.5,
                    0.5,
                    0.5
                ],
                [
                    0.5,
                    -0.5,
                    0.5
                ],
                [
                    0.5,
                    -0.5,
                    -0.5
                ],
                [
                    0.5,
                    0.5,
                    -0.5
                ],
                [
                    -0.5,
                    0.5,
                    -0.5
                ],
                [
                    -0.5,
                    -0.5,
                    -0.5
                ],
                [
                    0.5,
                    -0.5,
                    -0.5
                ],
                [
                    -0.5,
                    -0.5,
                    -0.5
                ],
                [
                    -0.5,
                    -0.5,
                    0.5
                ],
                [
                    -0.5,
                    0.5,
                    0.5
                ],
                [
                    -0.5,
                    -0.5,
                    0.5
                ],
                [
                    0.5,
                    -0.5,
                    0.5
                ]
            ],
            "degree": 1
        }
    ]

OCTO_CURVEDATA = [
        {
            "knots": [
                0.0,
                1.0,
                2.0,
                3.0,
                4.0,
                5.0,
                6.0,
                7.0,
                8.0,
                9.0,
                10.0,
                11.0,
                12.0,
                13.0
            ],
            "cvs": [
                [
                    0.0,
                    -2.220446049250313e-16,
                    1.0
                ],
                [
                    1.0,
                    0.0,
                    0.0
                ],
                [
                    0.0,
                    1.0,
                    2.220446049250313e-16
                ],
                [
                    0.0,
                    -2.220446049250313e-16,
                    1.0
                ],
                [
                    0.0,
                    -1.0,
                    -2.220446049250313e-16
                ],
                [
                    1.0,
                    0.0,
                    0.0
                ],
                [
                    0.0,
                    2.220446049250313e-16,
                    -1.0
                ],
                [
                    0.0,
                    1.0,
                    2.220446049250313e-16
                ],
                [
                    -1.0,
                    0.0,
                    0.0
                ],
                [
                    0.0,
                    -2.220446049250313e-16,
                    1.0
                ],
                [
                    0.0,
                    -1.0,
                    -2.220446049250313e-16
                ],
                [
                    -1.0,
                    0.0,
                    0.0
                ],
                [
                    0.0,
                    2.220446049250313e-16,
                    -1.0
                ],
                [
                    0.0,
                    -1.0,
                    -2.220446049250313e-16
                ]
            ],
            "degree": 1
        }
    ]