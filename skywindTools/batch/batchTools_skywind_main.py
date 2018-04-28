import batchTools_skywind
import batchTools_ui_skywind as ui
from Qt import QtWidgets, QtCore

window = None

def load():

    global window

    def batch(fileNames, directory, rig, script):

        config = batchTools_skywind.skywindBatchConfig(fileNames, directory, rig, script)
        config.batch()

    if window is None:

        app = QtWidgets.QApplication.instance()
        parent = {o.objectName(): o for o in app.topLevelWidgets()}["MayaWindow"]

        window = ui.skywindBatchWindow(parent)
        window.onBatch.connect(batch)

    window.show()