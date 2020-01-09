import numpy as np
import matplotlib.pyplot as plt

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QDateTime, QTimer
from PyQt5.QtGui import QPalette
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class mrsSpecChanell(QDialog):

    def __init__(self, parent=None):
        super(mrsSpecChanell, self).__init__(parent)

        #Create the canvas to load the plot
        self.createBottomPlot()

        topLambda = QHBoxLayout()
        topZ = QHBoxLayout()
        topFile= QVBoxLayout()

        #Create lambda widgets

        lambdaLabel = QLabel("λemit(μm): ")
        lambdaEdit = QLineEdit('')

        #Create Z widgets
        zLabel = QLabel("Z: ") 
        zEdit = QLineEdit('')

        #Create file open widgets 
        fileLabel = QLabel("File Spectrum [Wavelength [μm], Flux [uJy]]")
        fileLabel.setAlignment(Qt.AlignCenter)
        fileButton = QPushButton("Search file")
        fileButton.clicked.connect(lambda: self.searchFile(float(zEdit.text()), lambdaEdit.text()))

        #Set table sizes and margins
        self.filePrevTable = QTableWidget(5,2)

        self.filePrevTable.setHorizontalHeaderLabels(
            ["Wavelength [μm]", "Flux [uJy]"])
        header = self.filePrevTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        topLambda.addWidget(lambdaLabel)
        topLambda.addWidget(lambdaEdit)

        topZ.addWidget(zLabel)
        topZ.addWidget(zEdit)
        topZ.addStretch(2)

        topEditsLambda = QWidget(self)
        topEditsZ = QWidget(self)

        topEditsLambda.setLayout(topLambda)
        topEditsZ.setLayout(topZ)

        topFile.addWidget(topEditsLambda)
        topFile.addWidget(topEditsZ)
        topFile.addWidget(fileLabel)
        topFile.addWidget(fileButton)
        topFile.addWidget(self.filePrevTable)
        
        mainLayout = QGridLayout()

        mainLayout.addLayout(topFile, 0, 0, 1, 0)
        mainLayout.addWidget(self.bottomPlot, 1, 0)
        mainLayout.setRowStretch(1, 0)
        mainLayout.setColumnStretch(0, 0)

        self.setLayout(mainLayout)

        self.setWindowTitle("mrs_spec_chan.py")

    #Create the canvas to draw the plot
    def createBottomPlot(self):

        self.bottomPlot = QGroupBox("Plot")

        #Create a list of values for each channel
        self.subBandsValues = np.array([[4.87, 5.82], [5.62, 6.73], [6.49, 7.76], [7.45, 8.90], [8.61, 10.28], 
        [9.91, 11.87], [11.47, 13.67], [13.25, 15.80], [15.30, 18.24], [17.54, 21.10], [20.44, 24.72], [23.84, 28.82]])
        self.subBandsNames = np.array([["1A", "1B", "1C"],
                                        ["2A", "2B", "2C"], 
                                        ["3A", "3B", "3C"], 
                                        ["4A", "4B", "4C"]])

        #Add colors
        self.subBandsColors = np.array([["#d3ff00", "#00ff18", "#034500"],
                                        ["#439cfe", "#2673b8", "#2946bd"], 
                                        ["#ffbb3b", "#ffab0b", "#e19e1e"],
                                        ["#ff7373", "#f84031", "#94261d"]])

        self.figure = Figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)

        self.ax1 = self.figure.add_subplot(111)

        self.ax1.set_visible(False)

        self.bottomPlot.setLayout(layout)

    #Draw the axis
    def plot(self, waveL, fluxL, opWaveL, plotName):
        self.ax1.set_visible(True)
        # discards the old graph
        self.ax1.clear()

        #Draw MRS subbands on the plot
        for (x,y), value in np.ndenumerate(self.subBandsValues):
            
            if y == 0:
                self.ax1.axvline(
                    x=value, linestyle='--', color=self.subBandsColors[int(x/3), (x)%3])
            else:
                self.ax1.axvline(x=value, color=self.subBandsColors[int(x/3), (x) % 3], linestyle='--', 
                label=self.subBandsNames[int(x/3), (x) % 3])
                

        #Draw optional wave lengths
        for waveLenght in opWaveL:
            self.ax1.axvline(x=float(waveLenght), color="#ff1aa6")
            self.ax1.text(
                float(waveLenght), max(fluxL), 'λobs', rotation=0)

        #Set text and range of the axes
        self.ax1.set_title(plotName, pad= 20)
        self.ax1.set_xlabel("Wavelength range(μm)")

        self.ax1.set_ylabel("fx")

        self.ax1.set_xlim([5, 30])
        self.ax1.set_ylim([0, max(fluxL)])
        self.ax1.plot(waveL[0:len(waveL)-1], fluxL)
        self.ax1.grid()
        self.ax1.legend(loc= 'center left', bbox_to_anchor= (1, 0.5))

        self.figure.tight_layout(pad = 2)

        self.canvas.draw()

    def searchFile(self, z, opWave):
        waveLengthL = []
        fluxL = []

        fileSearch = QFileDialog()
        fileSearch.setFileMode(QFileDialog.AnyFile)
        fileSearch.setNameFilter("Text files (*.txt)")
        if fileSearch.exec_():
            filenames = fileSearch.selectedFiles()
            data = np.loadtxt(filenames[0], delimiter=' ')
            
            #Calculate the data shift for each value
            for (x,y), value in np.ndenumerate(data):

                if y == 0:
                    waveLengthL.append(float(value*(1+z)))
                else:
                    fluxL.append(float(value*(1+z)))

            #Inserte the first 5 rows of the array into the table for preview
            for i in range(0,5):
                waveLenght = QTableWidgetItem(str(waveLengthL[i]))
                flux = QTableWidgetItem(str(fluxL[i]))

                self.filePrevTable.setItem(i, 0, waveLenght)
                self.filePrevTable.setItem(i, 1, flux)

        waveLengthL = np.array(waveLengthL)
        fluxL = np.array(fluxL)
        waveLengthLSlice = waveLengthL[(waveLengthL >= 4.87) & (waveLengthL <= 28.82)]

        index1 = np.where(waveLengthL == np.amin(waveLengthLSlice))
        index2 = np.where(waveLengthL == np.amax(waveLengthLSlice))
        
        fluxL = fluxL[index1[0][0]:index2[0][0]]
        #Print the plot 
        self.plot(waveLengthLSlice, fluxL , opWave.split(",") if len(opWave) > 0 else [], filenames[0])

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    mrss = mrsSpecChanell()
    mrss.show()
    sys.exit(app.exec_())
