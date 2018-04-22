import batchTools_skywind
import batchTools_ui_skywind as ui
reload(ui)
reload(batchTools_skywind)

from Qt import QtWidgets, QtCore
from Qt.QtCore import Slot
import logging

window = None

@Slot(list, str, str, str, str)
def batch(fileNames, directory, rig, script, root_name):
    if fileNames is None:
        logging.error('No File Names Specified')
    elif directory is None:
        logging.error('No Directory Specified')
    elif rig is None:
        logging.error('No Rig Specified')
    else:
        config = batchTools_skywind.skywindBatchConfig(fileNames, directory, rig, script, root_name)
        config.batch()

@Slot(QtWidgets.QWidget)
def getSelected(widget):
    widget.value = batchTools_skywind.skywindBatchConfig.getSelected()

def load():

    global window

    if window is None:

        app = QtWidgets.QApplication.instance()
        parent = {o.objectName(): o for o in app.topLevelWidgets()}["MayaWindow"]

        window = ui.skywindBatchWindow(parent)
        window.onGetSelected.connect(getSelected)
        window.onBatch.connect(batch)

    window.show()