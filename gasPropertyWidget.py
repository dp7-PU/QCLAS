"""
Create line with five text edits.
"""
from PyQt4 import QtGui, QtCore
import sys


class gasLineEdit(QtGui.QWidget):
    def __init__(self, parent=None, dataList=[]):
        super(gasLineEdit, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.gasSelect = QtGui.QComboBox(parent)
        self.gasSelect.addItem('None')
        self.gasParams = {'gas': None, 'c': 0, 'p': 1000, 't': 296, 'l': 100}
        for gas in dataList:
            self.gasSelect.addItem(gas)

        cLE = QtGui.QLineEdit(parent)
        cLE.setText('0')
        pLE = QtGui.QLineEdit(parent)
        pLE.setText('1000')
        tLE = QtGui.QLineEdit(parent)
        tLE.setText('296')
        lLE = QtGui.QLineEdit(parent)
        lLE.setText('100')
        hbox = QtGui.QHBoxLayout()

        closeButton = QtGui.QPushButton('-')
        closeButton.setFixedWidth(20)
        closeButton.clicked.connect(self.closeup)

        pLE.textEdited[str].connect(self.assignP)
        tLE.textEdited[str].connect(self.assignT)
        lLE.textEdited[str].connect(self.assignL)
        cLE.textEdited[str].connect(self.assignC)
        self.gasSelect.activated[str].connect(self.assignGas)

        hbox.addWidget(self.gasSelect)
        hbox.addWidget(cLE)
        hbox.addWidget(pLE)
        hbox.addWidget(tLE)
        hbox.addWidget(lLE)
        hbox.addWidget(closeButton)
        hbox.setAlignment(QtCore.Qt.AlignLeft)
        hbox.setMargin(0)
        self.setLayout(hbox)

    def assignGas(self, text):
        try:
            self.gasParams['gas'] = str(text)
        except:
            pass

    def assignP(self, text):
        try:
            self.gasParams['p'] = float(text)
        except:
            pass

    def assignT(self, text):
        try:
            self.gasParams['t'] = float(text)
        except:
            pass

    def assignL(self, text):
        try:
            self.gasParams['l'] = float(text)
        except:
            pass

    def assignC(self, text):
        try:
            self.gasParams['c'] = float(text)
        except:
            pass

    def closeup(self):
        self.close()
        self.gasParams = None


class scrollPanel(QtGui.QWidget):
    def __init__(self, parent, gasList=[]):
        super(scrollPanel, self).__init__(parent)

        self.gasHandleList = []
        self.addButton = QtGui.QPushButton('Add Gas')
        self.addButton.clicked.connect(self.addGas)
        self.gasList = gasList
        headerWidget = QtGui.QWidget(self)
        hboxHeader = QtGui.QHBoxLayout()
        unitWidget = QtGui.QWidget(self)
        unitHBox = QtGui.QHBoxLayout()
        leGas = QtGui.QLabel('Gas')
        leC = QtGui.QLabel('C')
        leP = QtGui.QLabel('P ')
        leT = QtGui.QLabel('T ')
        leL = QtGui.QLabel('L ')
        leE = QtGui.QLabel('Delete')
        # leE.setFixedWidth()

        unitLabel = QtGui.QLabel('Unit: ')
        self.concUnit = QtGui.QComboBox()
        self.concUnit.addItems(['V ratio', 'mol/m^3'])
        self.pressUnit = QtGui.QComboBox()
        self.pressUnit.addItems(['hPa', 'kPa', 'Torr'])
        self.tempUnit = QtGui.QComboBox()
        self.tempUnit.addItems(['K', 'degC', 'degF'])
        self.lengthUnit = QtGui.QComboBox()
        self.lengthUnit.addItems(['cm', 'm', 'inch'])
        noneLabel = QtGui.QLabel(' ')

        # Header layout
        hboxHeader.addWidget(leGas)
        hboxHeader.addWidget(leC)
        hboxHeader.addWidget(leP)
        hboxHeader.addWidget(leT)
        hboxHeader.addWidget(leL)
        hboxHeader.addWidget(leE)
        hboxHeader.setSpacing(5)
        hboxHeader.setMargin(0)
        headerWidget.setLayout(hboxHeader)

        # Add widgets to unit row layout (2nd row)
        unitHBox.addWidget(unitLabel)
        unitHBox.addWidget(self.concUnit)
        unitHBox.addWidget(self.pressUnit)
        unitHBox.addWidget(self.tempUnit)
        unitHBox.addWidget(self.lengthUnit)
        unitHBox.addWidget(noneLabel)
        unitHBox.setSpacing(5)
        unitHBox.setMargin(0)
        unitWidget.setLayout(unitHBox)

        # scroll area widget contents - layout
        self.vbox = QtGui.QVBoxLayout()
        self.vbox.setAlignment(QtCore.Qt.AlignTop)
        self.vbox.addWidget(headerWidget)
        self.vbox.addWidget(unitWidget)
        # scroll area widget contents
        self.scrollWidget = QtGui.QWidget()
        self.scrollWidget.setLayout(self.vbox)

        # scroll area
        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollWidget)
        # self.scrollArea.setMinimumWidth(480)

        # main layout
        self.mainLayout = QtGui.QVBoxLayout()

        # add all main to the main vLayout
        self.mainLayout.addWidget(self.addButton)
        self.mainLayout.addWidget(self.scrollArea)

        self.setLayout(self.mainLayout)

        self.resize(600, 600)

    def addGas(self):
        gasLayout = gasLineEdit(self, dataList=self.gasList)
        self.gasHandleList.append(gasLayout)
        self.vbox.addWidget(gasLayout)

    def updateAll(self):
        for gasHandle in self.gasHandleList:
            if gasHandle.gasParams is not None:
                gasHandle.gasSelect.clear()
                gasHandle.gasSelect.addItem('None')
                print(self.gasList)
                gasHandle.gasSelect.addItems(self.gasList)
            else:
                self.gasHandleList.remove(gasHandle)

    def getGasInfo(self):
        gasParamsList = []
        for gasHandle in self.gasHandleList:
            if gasHandle.gasParams is not None:
                print gasHandle.gasParams
                gasParamsList.append(gasHandle.gasParams)
            else:
                self.gasHandleList.remove(gasHandle)
        return gasParamsList


def main():
    app = QtGui.QApplication(sys.argv)
    ex = scrollPanel(None)
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
