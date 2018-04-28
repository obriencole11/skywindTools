from .vendor.Qt import QtWidgets, QtGui, QtCore
from .vendor.Qt.QtCore import Signal, Slot

class RetargeterWindow(QtWidgets.QMainWindow):

    bindClicked = Signal(float, bool, bool, bool, bool)
    bakeClicked = Signal()
    selectNodesClicked = Signal()
    removeClicked = Signal()
    addIkControlClicked = Signal()

    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)

        ### Main ###

        # Set the window title
        self.setWindowTitle('Retargeter')

        # Create the main widget
        mainWidget = QtWidgets.QWidget()
        self.setCentralWidget(mainWidget)

        # Create the mainlayout
        mainLayout = QtWidgets.QVBoxLayout()
        mainWidget.setLayout(mainLayout)


        ### Settings ###

        # Create a group box for the settings
        settingsBox = QtWidgets.QGroupBox('Settings', mainWidget)
        mainLayout.addWidget(settingsBox)

        # Create a form layout for setttings
        settingLayout = QtWidgets.QFormLayout()
        settingLayout.setLabelAlignment(QtCore.Qt.AlignRight)
        settingsBox.setLayout(settingLayout)

        # Snap to target setting
        self.snapTranslateBox = QtWidgets.QCheckBox(settingsBox)
        self.snapTranslateBox.setChecked(True)
        settingLayout.addRow('Preserve Translation', self.snapTranslateBox)

        self.snapRotateBox = QtWidgets.QCheckBox(settingsBox)
        self.snapRotateBox.setChecked(True)
        settingLayout.addRow('Preserve Rotation', self.snapRotateBox)

        # Node Scale setting
        self.scaleLine = QtWidgets.QLineEdit(settingsBox)
        self.scaleLine.setValidator(QtGui.QDoubleValidator(0, 100, 2, self))
        self.scaleLine.setText('1.0')
        settingLayout.addRow('Node Scale', self.scaleLine)


        ### Buttons ###

        # Bind Button Group box
        bindGroupBox = QtWidgets.QGroupBox('Binding', mainWidget)
        mainLayout.addWidget(bindGroupBox)

        # Button layout
        bindLayout = QtWidgets.QGridLayout()
        bindGroupBox.setLayout(bindLayout)

        # Bind button
        bindTranslateButton = QtWidgets.QPushButton('Bind Translate', mainWidget)
        bindTranslateButton.clicked.connect(self.bindTranslate)
        #mainLayout.addWidget(bindTranslateButton)
        bindLayout.addWidget(bindTranslateButton, 0,0)


        bindBothButton = QtWidgets.QPushButton('Bind Both', mainWidget)
        bindBothButton.clicked.connect(self.bindBoth)
        #mainLayout.addWidget(bindBothButton)
        bindLayout.addWidget( bindBothButton, 0,1)

        bindRotateButton = QtWidgets.QPushButton('Bind Rotate', mainWidget)
        bindRotateButton.clicked.connect(self.bindRotate)
        #mainLayout.addWidget(bindRotateButton)
        bindLayout.addWidget(bindRotateButton, 1,0, 1,2)


        # Node Control Group Box
        nodeGroupBox = QtWidgets.QGroupBox('Node Control', mainWidget)
        mainLayout.addWidget(nodeGroupBox)

        # Node Layout
        nodeLayout = QtWidgets.QGridLayout()
        nodeGroupBox.setLayout(nodeLayout)

        # Select nodes button
        selectButton = QtWidgets.QPushButton('Select Bind Nodes', mainWidget)
        selectButton.clicked.connect(self.selectNodesClicked)
        nodeLayout.addWidget(selectButton, 2,0,1,2)

        # Bake nodes button
        bakeButton = QtWidgets.QPushButton('Bake Bind Targets', mainWidget)
        bakeButton.clicked.connect(self.bakeClicked)
        nodeLayout.addWidget( bakeButton, 3,0,1,2)


        # Rigging Group Box
        rigGroupBox = QtWidgets.QGroupBox('Rigging', mainWidget)
        mainLayout.addWidget(rigGroupBox)

        # Node Layout
        rigLayout = QtWidgets.QGridLayout()
        rigGroupBox.setLayout(rigLayout)

        # Select nodes button
        ikButton = QtWidgets.QPushButton('Add IK Controls', mainWidget)
        ikButton.clicked.connect(self.addIkControlClicked)
        rigLayout.addWidget(ikButton, 2, 0, 1, 2)


    @Slot()
    def bindTranslate(self):
        self.bindClicked.emit(float(self.scaleLine.text()),
                                    True, False,
                                    self.snapTranslateBox.checkState(),
                                    self.snapRotateBox.checkState())

    @Slot()
    def bindRotate(self):
        self.bindClicked.emit(float(self.scaleLine.text()),
                              False, True,
                              self.snapTranslateBox.checkState(),
                              self.snapRotateBox.checkState())

    @Slot()
    def bindBoth(self):
        self.bindClicked.emit(float(self.scaleLine.text()),
                              True, True,
                              self.snapTranslateBox.checkState(),
                              self.snapRotateBox.checkState())


window = None

def _testUI():

    # Create a reference to the application
    app = QtWidgets.QApplication([])

    # Create the window and show it
    window = RetargeterWindow()
    window.show()

    # Begin the event loop
    app.exec_()

if __name__ == '__main__':
    _testUI()