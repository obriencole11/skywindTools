from Qt import QtWidgets, QtCore
from Qt.QtCore import Signal, Slot
import batchTools_ui
reload(batchTools_ui)

class skywindBatchWindow(batchTools_ui.batchWindow):

    onBatch = Signal(list, str, str, str, str)
    onGetSelected = Signal(QtWidgets.QWidget)

    def __init__(self, *args, **kwargs):
        batchTools_ui.batchWindow.__init__(self, *args, **kwargs)

        self.setWindowTitle('Skywind Batch Retarget')

    def _setupSettings(self):

        # Set up the base settings
        batchTools_ui.batchWindow._setupSettings(self)

        # Add a setting for selecting a rig file
        self.rig = batchTools_ui.fileDirectoryWidget(self.settingsGroup)
        self.settingsLayout.addRow('Rig File', self.rig)

        # Add a setting for selecting a between batch script
        self.script = batchTools_ui.fileDirectoryWidget(self.settingsGroup)
        self.settingsLayout.addRow('Batch Script', self.script)

        self.root_name = batchTools_ui.nodeNameWidget(self.settingsGroup)
        self.root_name.OnGetSelected.connect(self.onGetSelected)
        self.settingsLayout.addRow('Root Name', self.root_name)

    def onBatchClicked(self):
        self.onBatch.emit(self.source.value, self.destination.value, self.rig.value, self.script.value,
                          self.root_name.value)

if __name__ == '__main__':

    app = QtWidgets.QApplication([])

    win = skywindBatchWindow()
    win.show()

    app.exec_()