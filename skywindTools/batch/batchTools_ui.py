from Qt import QtWidgets, QtCore
from Qt.QtCore import Signal, Slot
import os

class nodeNameWidget(QtWidgets.QWidget):

    OnGetSelected = Signal(QtWidgets.QWidget)

    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)

        # Create the layout for the widget
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(5,1,5,1)
        self.setLayout(layout)

        # Line edit to display
        self.lineEdit = QtWidgets.QLineEdit(self)
        layout.addWidget(self.lineEdit)

        # Push Button to create popup window
        button = QtWidgets.QPushButton('+', self)
        button.setMaximumWidth(30)
        button.clicked.connect(self.addSelected)
        layout.addWidget(button)

        self.addSelected()

    def addSelected(self):
        self.OnGetSelected.emit(self)

    @property
    def value(self):
        try:
            return self.lineEdit.text()
        except AttributeError:
            return None

    @value.setter
    def value(self, value):
        self.lineEdit.setText(value)

class directoryWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)

        # Create the layout for the widget
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(5,1,5,1)
        self.setLayout(layout)

        # Line edit to display
        self.lineEdit = QtWidgets.QLineEdit(self)
        layout.addWidget(self.lineEdit)

        # Push Button to create popup window
        button = QtWidgets.QPushButton('...', self)
        button.setMaximumWidth(30)
        button.clicked.connect(self.showPopup)
        layout.addWidget(button)

    def showPopup(self):

        fileDialog = QtWidgets.QFileDialog()

        # Grab the name of the directory
        self._value = fileDialog.getExistingDirectory(self)
        self.lineEdit.setText(self._value)

    @property
    def value(self):
        try:
            return self._value
        except AttributeError:
            return None

class fileDirectoryWidget(directoryWidget):
    def __init__(self, *args, **kwargs):
        directoryWidget.__init__(self, *args, **kwargs)

    def showPopup(self):
        fileDialog = QtWidgets.QFileDialog()

        # Grab the name of the directory
        self._value, _ = fileDialog.getOpenFileName(self)
        self.lineEdit.setText(self._value)

class multiFileDirectoryWidget(directoryWidget):

    def __init__(self, *args, **kwargs):
        directoryWidget.__init__(self, *args, **kwargs)

    def showPopup(self):
        fileDialog = QtWidgets.QFileDialog()

        # Grab the name of the directory
        self._value, _ = fileDialog.getOpenFileNames(self)
        nameList = [os.path.basename(value) for value in self._value]
        self.lineEdit.setText(', '.join(nameList))

class batchWindow(QtWidgets.QMainWindow):

    onBatch = Signal(list, str)
    onGetSelected = Signal()

    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)

        # Set the window title
        self.setWindowTitle('Batch Export')

        # Create the central widget
        self.mainWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.mainWidget)

        # Create the window layout
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainWidget.setLayout(self.mainLayout)

        # Create the settings widgets
        self._setupSettings()

        # The button to initiate the batch
        batchButton = QtWidgets.QPushButton('Batch', self)
        batchButton.clicked.connect(self.onBatchClicked)
        self.mainLayout.addWidget(batchButton)

    def _setupSettings(self):

        # Create a groupBox to house the settings
        self.settingsGroup = QtWidgets.QGroupBox('Settings', self.mainWidget)
        self.mainLayout.addWidget(self.settingsGroup)

        # Create a layout for the settings
        self.settingsLayout = QtWidgets.QFormLayout()
        self.settingsGroup.setLayout(self.settingsLayout)

        # Source directory widget
        self.source = multiFileDirectoryWidget(self.mainWidget)
        self.settingsLayout.addRow('Source Files', self.source)

        # Destination directory widget
        self.destination = directoryWidget(self.mainWidget)
        self.settingsLayout.addRow('Destination', self.destination)

    def onBatchClicked(self):
        self.onBatch.emit(self.source.value, self.destination.value)


@Slot(str, list)
def batch(string, list):
    print string
    print list

if __name__ == '__main__':

    app = QtWidgets.QApplication([])

    win = batchWindow()
    win.onBatch.connect(batch)
    win.show()

    app.exec_()

