import retargeter
import retargeter_ui as ui
from .vendor.Qt import QtWidgets

window = None

def show():

    global window

    if window:
        window.close()

    # Grab the maya application and the main maya window
    app = QtWidgets.QApplication.instance()
    mayaWindow = {o.objectName(): o for o in app.topLevelWidgets()}["MayaWindow"]

    # Create the window
    window = ui.RetargeterWindow(mayaWindow)

    # Connect window signals
    window.bindClicked.connect(retargeter.bindSelected)
    window.bakeClicked.connect(retargeter.bakeBindTargets)
    window.selectNodesClicked.connect(retargeter.selectBindNodes)
    window.removeClicked.connect(retargeter.removeSelectedNodes)
    window.addIkControlClicked.connect(retargeter.buildIKChainSelected)

    window.show()