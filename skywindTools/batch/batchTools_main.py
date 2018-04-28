import batchTools
import batchTools_ui as ui
import logging
from Qt import QtWidgets, QtCore
from Qt.QtCore import Slot

window = None

@Slot(list, str)
def batch(fileNames, directory):

    if fileNames is None:
        logging.error('No File Names Specified')
    elif directory is None:
        logging.error('No Directory Specified')
    else:
        config = batchTools.batchConfig(fileNames, directory)
        config.batch()

def load():

    global window

    if window:
        window.close()

    app = QtWidgets.QApplication.instance()
    parent = {o.objectName(): o for o in app.topLevelWidgets()}["MayaWindow"]

    window = ui.batchWindow(parent)
    window.onBatch.connect(batch)
    window  .show()