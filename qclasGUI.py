"""
Make a GUI for qclas. This program uses HAPI to generate absorption profiles.
The program comes in without HITRAN data files. User can use the program to
download lines they need.

GUI of the program is based on PyQt4.

Da Pan, v-alpha, started on 02/13/2016
"""

import hapi
import numpy as np
from PyQt4 import QtGui, QtCore
import sys
import os
import gasPropertyWidget
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import \
    NavigationToolbar2QT as NavigationToolbar
import specCal
from matplotlib.externals import six
import matplotlib


class mplCanvas(QtGui.QWidget):
    def __init__(self, parent=None, width=5, height=4, dpi=100, bgcolor='#ffffff'):
        super(mplCanvas, self).__init__(parent)

        # a figure instance to plot on
        self.figure = plt.figure(figsize=(width, height), dpi=dpi, facecolor=bgcolor)
        self.axes = self.figure.add_subplot(111)
        self.axes.hold(False)
        self.index = 0
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        FigureCanvas.setSizePolicy(self.canvas,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Just some plotButton connected to `plot` method
        self.plotButton = QtGui.QPushButton('Plot', parent=self)
        self.exportButton = QtGui.QPushButton('Export', parent=self)

        # set the layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        buttonHBox = QtGui.QHBoxLayout()
        buttonHBox.addWidget(self.plotButton)
        buttonHBox.addWidget(self.exportButton)
        layout.addLayout(buttonHBox)
        self.setLayout(layout)


class AppWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(AppWindow, self).__init__(parent)
        self.setWindowTitle('QCLAS')
        self.scrsz = QtGui.QDesktopWidget().availableGeometry().getRect()
        self.dpi = int(self.scrsz[2] / 25)
        self.initUI()

    def resizeEvent(self, resizeEvent):
        self.updateCanvasGeometry()

    def initUI(self):
        # Action: set HAPI database Directory

        self.initMenu()
        self.gasListLabel = QtGui.QLabel()
        self.calGasList = []
        self.canvasList = []
        self.setGasListLabel()
        self.statusBar().addPermanentWidget(self.gasListLabel)
        self.mainWidget = QtGui.QWidget()
        self.setFrames()
        self.setLeftColumn()
        self.setCanvas()
        self.laserSpec = None

        self.setCentralWidget(self.mainWidget)
        self.resize(0.8 * self.scrsz[2], 0.8 * self.scrsz[3])

    def initMenu(self):
        # HITRAN Data menu
        chHapiDir = QtGui.QAction('&Change HITRAN Dir', self)
        chHapiDir.triggered.connect(self.setHapiDir)
        dnldData = QtGui.QAction('&Download HITRAN Data', self)
        dnldData.triggered.connect(self.fetchData)
        saveHData = QtGui.QAction('&Save HITRAN Data', self)
        saveHData.triggered.connect(self.commitHData)
        listHData = QtGui.QAction('Available HITRAN Data', self)
        listHData.triggered.connect(self.listHData)

        self.HapiMenu = QtGui.QMenu('&HITRAN Data', self)
        self.HapiMenu.addAction(chHapiDir)
        self.HapiMenu.addAction(dnldData)
        self.HapiMenu.addAction(saveHData)
        self.HapiMenu.addAction(listHData)

        # Laser setting menu
        loadLaserFile = QtGui.QAction('&Load laser config', self)
        loadLaserFile.triggered.connect(self.getLaserConfig)

        self.laserMenu = QtGui.QMenu('&Laser Config')
        self.laserMenu.addAction(loadLaserFile)

        # Save results menu
        # saveResults = QtGui.QAction('&')

        self.menuBar().addMenu(self.HapiMenu)
        self.menuBar().addMenu(self.laserMenu)

    ##### BLOCK 1: HAPI data management

    def getLaserConfig(self):
        fileName = self.getFileNameDialog()
        self.laserSpec = specCal.read_config(fileName)

    def getFileNameDialog(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self)
        return fileName

    def getFileDirDialog(self):
        DirName = QtGui.QFileDialog.getExistingDirectory(self)
        return DirName

    def getGasList(self):
        self.gasList = hapi.getTableList()
        hapi.getTableList()
        self.gasList.remove('sampletab')

    def setGasListLabel(self):
        self.getGasList()
        if len(self.gasList) == 0:
            self.gasListLabel.setText('No Data')
        else:
            self.gasListLabel.setText('Data ready for: ' + ', '.join(self.gasList))

    def setHapiDir(self):
        dbDir = self.getFileDirDialog()
        hapi.db_begin_pickle(dbDir)
        for gas in self.gasList:
            hapi.dropTable(gas)
        self.gasList = []
        self.setGasListLabel()
        self.scrollGasPanel.gasList = self.gasList
        self.scrollGasPanel.updateAll()
        hapi.tableList()

    def fetchData(self):
        inputStr, ok = QtGui.QInputDialog.getText(self, 'Add data',
                                                  "Temporarily add data to the database; the data will not be saved." +
                                                  "\nLarge database will slow down loading processes when start the program." +
                                                  "\nTo Save the data, use 'Save HITRAN data'." +
                                                  "\n\nEnter Gas name, min, and max wavenumber separated by ',' (e.g. H2O,1000,2000)")

        if ok:
            params = str(inputStr).split(',')
            for i in range(40):
                try:
                    name = hapi.moleculeName(i + 1)
                    if name == params[0]:
                        M = i + 1
                        print M
                except:
                    pass
            # try:
            print params[0]
            hapi.fetch_pickle(params[0], M, 1, int(params[1]), int(params[2]))
            nu = hapi.getColumn(params[0], 'nu')
            self.statusBar().showMessage(
                str(len(nu)) + ' lines' + ' added for ' + params[0] + ' ' + params[
                    1] + '<nu<' + params[2])
            # except:
            #     self.statusBar().showMessage('Data fetch failed')
        self.setGasListLabel()
        self.scrollGasPanel.gasList = self.gasList
        self.scrollGasPanel.updateAll()

    def commitHData(self):
        hapi.db_commit_pickle()
        self.statusBar().showMessage('HITRAN data saved')

    ##### End of BLOCK 1.

    def setWaveRangeWidget(self):
        # TODO add cm-1, nm, um conversion
        self.waveRangeWidget = QtGui.QWidget(self.mainWidget)
        hbox = QtGui.QHBoxLayout()
        label1 = QtGui.QLabel('Nu range: ')
        label2 = QtGui.QLabel('to')
        self.minNu = QtGui.QLineEdit(self.mainWidget)
        self.minNu.setText('1000')
        self.minNu.setMaximumWidth(90)
        self.maxNu = QtGui.QLineEdit(self.mainWidget)
        self.maxNu.setText('1100')
        self.maxNu.setMaximumWidth(90)
        hbox.addWidget(label1)
        hbox.addWidget(self.minNu)
        hbox.addWidget(label2)
        hbox.addWidget(self.maxNu)
        labelNumPt = QtGui.QLabel('; # of point: ')
        self.numPt = QtGui.QLineEdit(self.mainWidget)
        self.numPt.setText('1000')
        self.numPt.setMaximumWidth(70)
        hbox.addWidget(labelNumPt)
        hbox.addWidget(self.numPt)
        hbox.setAlignment(QtCore.Qt.AlignLeft)
        hbox.setMargin(0)
        self.waveRangeWidget.setLayout(hbox)

    def setSpecWidget(self):
        self.specWidget = QtGui.QWidget(self.mainWidget)
        hbox = QtGui.QHBoxLayout()
        labelWhatPlot = QtGui.QLabel('   Plot: ')
        self.specChecks = QtGui.QButtonGroup(self.mainWidget)
        wmsCheck = QtGui.QRadioButton(self.mainWidget)
        dasCheck = QtGui.QRadioButton(self.mainWidget)
        wmsCheck.setText('WMS')
        dasCheck.setText('DAS')
        dasCheck.clicked.connect(self.chComboWhatPlot)
        wmsCheck.clicked.connect(self.chComboWhatPlot)
        self.comboWhatPlot = QtGui.QComboBox(self.mainWidget)
        self.specChecks.addButton(dasCheck, 1)
        self.specChecks.addButton(wmsCheck, 2)
        dasCheck.setChecked(True)
        self.chComboWhatPlot()
        hbox.addWidget(dasCheck)
        hbox.addWidget(wmsCheck)
        hbox.addWidget(labelWhatPlot)
        hbox.addWidget(self.comboWhatPlot)
        hbox.setAlignment(QtCore.Qt.AlignLeft)
        hbox.setMargin(0)
        hbox.setSpacing(10)
        self.specWidget.setLayout(hbox)

    def setLineShapeWidget(self):
        self.lineShapeWidget = QtGui.QWidget(self.mainWidget)
        lineShapeLabel = QtGui.QLabel('Line shape profile: ')
        self.comboLineShape = QtGui.QComboBox(self.mainWidget)
        self.comboLineShape.addItems(['Voigt', 'HT', 'Lorentz', 'Doppler'])
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(lineShapeLabel)
        hbox.addWidget(self.comboLineShape)
        hbox.setAlignment(QtCore.Qt.AlignLeft)
        hbox.setMargin(0)
        self.lineShapeWidget.setLayout(hbox)

    def setNumPanelWidget(self):
        self.numPanelWidget = QtGui.QWidget()
        self.numPanel = QtGui.QButtonGroup(self.mainWidget)
        onePanel = QtGui.QRadioButton(self.mainWidget)
        onePanel.setText('1')
        onePanel.setChecked(True)
        onePanel.clicked.connect(self.setCanvas)

        twoPanel = QtGui.QRadioButton(self)
        twoPanel.setText('2')
        twoPanel.clicked.connect(self.setCanvas)

        fourPanel = QtGui.QRadioButton(self)
        fourPanel.setText('4')
        fourPanel.clicked.connect(self.setCanvas)

        numLabel = QtGui.QLabel('# of panel: ')

        self.plotTotalCheck = QtGui.QCheckBox('Plot total')
        self.plotTotalCheck.setChecked(True)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(numLabel)
        hbox.addWidget(onePanel)
        hbox.addWidget(twoPanel)
        hbox.addWidget(fourPanel)
        hbox.addWidget(self.plotTotalCheck)
        self.numPanel.addButton(onePanel, 1)
        self.numPanel.addButton(twoPanel, 2)
        self.numPanel.addButton(fourPanel, 4)
        hbox.setAlignment(QtCore.Qt.AlignLeft)
        hbox.setMargin(0)
        self.numPanelWidget.setLayout(hbox)

    def setWmsMethodWidget(self):
        self.wmsMethodWidget = QtGui.QWidget(self.mainWidget)
        hbox = QtGui.QHBoxLayout()
        labelWmsMethod = QtGui.QLabel('WMS calculation method: ')
        self.wmsMethod = QtGui.QComboBox(self.mainWidget)
        self.wmsMethod.addItem('Theoretical', 1)
        self.wmsMethod.addItem('Simulation w/ params', 2)
        hbox.addWidget(labelWmsMethod)
        hbox.addWidget(self.wmsMethod)
        hbox.setMargin(0)
        self.wmsMethodWidget.setLayout(hbox)

    def setWmsModWidget(self):
        self.wmsModWidget = QtGui.QWidget(self.mainWidget)
        hbox = QtGui.QHBoxLayout()
        labelWmsMod = QtGui.QLabel('WMS modulation: ')
        labelModUnit = QtGui.QLabel('cm -1')
        self.leWmsMod = QtGui.QLineEdit('0.01')
        hbox.addWidget(labelWmsMod)
        hbox.addWidget(self.leWmsMod)
        hbox.addWidget(labelModUnit)
        hbox.setMargin(0)
        self.wmsModWidget.setLayout(hbox)

    def setICutWidget(self):
        self.iCutWidget = QtGui.QWidget(self.mainWidget)
        hbox = QtGui.QHBoxLayout()
        labelIcut = QtGui.QLabel('Intensity threshold: ')
        labelIcut.setMaximumWidth(150)
        self.leICut = QtGui.QLineEdit(self.mainWidget)
        self.leICut.setText('1e-30')
        self.leICut.setMaximumWidth(90)
        self.leICut.setAlignment(QtCore.Qt.AlignLeft)
        hbox.addWidget(labelIcut)
        hbox.addWidget(self.leICut)
        hbox.setSpacing(10)
        hbox.setMargin(0)
        hbox.setAlignment(QtCore.Qt.AlignLeft)
        self.iCutWidget.setLayout(hbox)

    def setLeftColumn(self):
        vboxTop = QtGui.QVBoxLayout()
        vboxBottom = QtGui.QVBoxLayout()

        self.scrollGasPanel = gasPropertyWidget.scrollPanel(self.mainWidget,
                                                            gasList=self.gasList)
        self.setWaveRangeWidget()
        self.setSpecWidget()
        self.setWmsMethodWidget()
        self.setWmsModWidget()
        self.setLineShapeWidget()
        self.setICutWidget()
        self.setNumPanelWidget()

        vboxBottom.addWidget(self.waveRangeWidget)
        vboxBottom.addWidget(self.specWidget)
        vboxBottom.addWidget(self.wmsMethodWidget)
        vboxBottom.addWidget(self.wmsModWidget)
        vboxBottom.addWidget(self.lineShapeWidget)
        vboxBottom.addWidget(self.iCutWidget)
        vboxBottom.addWidget(self.numPanelWidget)
        vboxBottom.setAlignment(QtCore.Qt.AlignTop)
        vboxTop.addWidget(self.scrollGasPanel)

        self.leftTop.setLayout(vboxTop)
        self.leftBottom.setLayout(vboxBottom)

    def genUnitDict(self):
        """
        Generate unit dict to be passed down to specCal.
        Returns
        -------
        unitDict: dict
            A dict has following keys: 'c', 'p', 't', 'l'
        """
        unitDict = {}
        unitDict['c'] = str(self.scrollGasPanel.concUnit.currentText())
        unitDict['p'] = str(self.scrollGasPanel.pressUnit.currentText())
        unitDict['t'] = str(self.scrollGasPanel.tempUnit.currentText())
        unitDict['l'] = str(self.scrollGasPanel.lengthUnit.currentText())

        return unitDict

    def setCanvas(self):
        numPanel = self.numPanel.checkedId()
        self.grid = QtGui.QGridLayout()
        for canvas in self.canvasList:
            self.grid.removeWidget(canvas)
            canvas.deleteLater()
            canvas.close()
            canvas.setParent(None)
        self.canvasList = []
        self.resultList = []

        position = [[1, 0], [2, 0], [1, 1], [2, 1]]
        for i in range(numPanel):
            canvas = mplCanvas(self, dpi=self.dpi)
            canvas.plotButton.clicked.connect(self.calPlot)
            canvas.exportButton.clicked.connect(self.exportData)
            canvas.index = i
            self.canvasList.append(canvas)
            self.resultList.append({})
            self.grid.addWidget(canvas, position[i][0], position[i][1])
            # canvas.draw()
        self.vboxRight.addLayout(self.grid)

    def chComboWhatPlot(self):
        if self.specChecks.checkedId() == 1:
            self.comboWhatPlot.clear()
            self.comboWhatPlot.addItem('Absorp coeff')
            self.comboWhatPlot.addItem('Absorbance')
            self.comboWhatPlot.addItem('Transmission')
        else:
            self.comboWhatPlot.clear()
            for i in range(12):
                self.comboWhatPlot.addItem(str(i + 1) + 'f')

    def setFrames(self):
        self.leftTop = QtGui.QGroupBox(self.mainWidget)
        self.leftTop.setTitle('Set gas properties')
        self.leftBottom = QtGui.QGroupBox(self.mainWidget)
        self.leftBottom.setTitle('Set plot properties')

        self.right = QtGui.QGroupBox(self.mainWidget)
        self.right.setTitle('Results')
        self.vboxRight = QtGui.QVBoxLayout()
        self.right.setLayout(self.vboxRight)

        self.split1 = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.split1.addWidget(self.leftTop)
        self.split1.addWidget(self.leftBottom)

        self.split2 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.split2.addWidget(self.split1)
        self.split2.addWidget(self.right)
        self.split2.setStretchFactor(1, 2)

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.split2)
        self.mainWidget.setLayout(hbox)

    def showError(self, errStr, details):
        errBox = QtGui.QMessageBox(self)
        errBox.setIcon(QtGui.QMessageBox.Information)

        errBox.setText(errStr)
        errBox.setDetailedText(details)
        errBox.setWindowTitle('Error message')
        errBox.setStandardButtons(QtGui.QMessageBox.Ok)

    def calPlot(self):
        canvas = self.sender().parent()
        print canvas.index
        unitDict = self.genUnitDict()
        nuMin = float(self.minNu.text())
        nuMax = float(self.maxNu.text())
        numPt = int(self.numPt.text())
        nu = np.linspace(nuMin, nuMax, numPt)
        iCut = float(self.leICut.text())
        gasParamsList = self.scrollGasPanel.getGasInfo()
        profile = self.comboLineShape.currentText()
        mode = self.comboWhatPlot.currentText()
        self.statusBar().showMessage('Calculating...')
        if self.specChecks.checkedId() == 1:
            dasResults = specCal.calDas(gasParamsList, nu, profile, mode,
                                        iCut=iCut, unitDict=unitDict)
            if type(dasResults) is str:
                errorMessage = QtGui.QMessageBox()
                errorMessage.setText(dasResults)
                errorMessage.exec_()
                self.statusBar().showMessage(dasResults)
            else:
                specCal.plotDas(canvas.axes, dasResults, mode,
                                showTotal=self.plotTotalCheck.isChecked(),
                                unitDict=unitDict)
                self.statusBar().showMessage('Done.')
            self.resultList[canvas.index] = dasResults

        else:
            method = self.wmsMethod.currentText()
            dNu = float(self.leWmsMod.text())
            nf = int(mode.replace('f', ''))
            if method == 'Theoretical':
                wmsResults = specCal.calWms(gasParamsList, nu, profile, nf, method,
                                            dNu=dNu, unitDict=unitDict)
            else:
                if self.laserSpec is None:
                    self.showError('No laser configuration.', 'Please go to Laser '
                                                              'config and load a '
                                                              'laser configuration.')
                    wmsResults = 'No laser configuration.'
                else:
                    self.laserSpec['central_wavelength'] = (nuMin + nuMax) / 2.
                    self.laserSpec['aRamp'] = (nuMax -
                                               nuMin) / 200 * 1e3 / self.laserSpec[
                                                  'tRamp']
                    wmsResults = specCal.calWms(gasParamsList, nu, profile, nf,
                                                'Simulation with parameters',
                                                laserSpec=self.laserSpec,
                                                unitDict=unitDict)
            if type(wmsResults) is str:
                errorMessage = QtGui.QMessageBox()
                errorMessage.setText(wmsResults)
                errorMessage.exec_()
                self.statusBar().showMessage(wmsResults)
            else:
                self.statusBar().showMessage('Done.')
                specCal.plotWms(canvas.axes, wmsResults,
                                showTotal=self.plotTotalCheck.isChecked())
            self.resultList[canvas.index] = wmsResults

        canvas.figure.tight_layout()
        canvas.canvas.draw()
        canvas.canvas.updateGeometry()

    def exportData(self):
        canvas = self.sender().parent()
        filename, pat = QtGui.QFileDialog.getSaveFileNameAndFilter(self, "Export "
                                                                         "data "
                                                                         "to csv file",
                                                                   "output.csv",
                                                                   filter=self.tr(
                                                                       "CSV "
                                                                       "files (*.csv)"))
        specCal.csvOutput(filename, self.resultList[canvas.index])

    def updateCanvasGeometry(self):
        for canvas in self.canvasList:
            canvas.figure.tight_layout()
            canvas.canvas.updateGeometry()

    def listHData(self):
        dialog = QtGui.QDialog(self.mainWidget)
        vboxScroll = QtGui.QVBoxLayout()
        scrollWidget = QtGui.QWidget(self.mainWidget)
        scrollArea = QtGui.QScrollArea(self.mainWidget)
        closeButton = QtGui.QPushButton('Close')
        closeButton.clicked.connect(dialog.close)
        vboxDialog = QtGui.QVBoxLayout()
        for gas in self.gasList:
            nu = np.array(hapi.getColumn(gas, 'nu'))
            gasInfo = gas + ' :' + str(nu.min()) + ' to ' + str(nu.max()) + ' cm -1'
            labelGasInfo = QtGui.QLabel(gasInfo)
            vboxScroll.addWidget(labelGasInfo)
        vboxScroll.setAlignment(QtCore.Qt.AlignTop)
        scrollWidget.setLayout(vboxScroll)
        scrollArea.setWidget(scrollWidget)
        vboxDialog.addWidget(scrollArea)
        vboxDialog.addWidget(closeButton)
        dialog.setWindowTitle('Available HITRAN data')
        dialog.setMinimumWidth(0.3 * self.scrsz[2])
        dialog.setLayout(vboxDialog)
        dialog.show()


def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)


def main():
    filename = 'defaultSettings.txt'
    app = QtGui.QApplication(sys.argv)
    appWindow = AppWindow()
    appWindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
