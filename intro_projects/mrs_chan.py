import matplotlib.pyplot as plt
import numpy as np

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QDateTime, QTimer
from PyQt5.QtGui import QPalette
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class mrsChanell(QDialog):

    def __init__(self, parent = None):
        super(mrsChanell, self).__init__(parent)
        
        #Create the widgets to save and plot the results
        self.createMidGroupBox()
        self.createBottomPlot()
        
        #Add the widgets that allow to insert values
        topLayout = QHBoxLayout()

        lambdaLabel = QLabel("λemit:")
        lambdaUnitLabel = QLabel("μm")
        lambdaEdit = QLineEdit('')

        zLabel = QLabel("z:")
        zEdit = QLineEdit('')

        #Left, top, right, bottom
        lambdaUnitLabel.setContentsMargins(0,0,40,0)

        chanellButton = QPushButton("Calculate")
        chanellButton.setDefault(True)
        chanellButton.clicked.connect(lambda: self.printResults(lambdaEdit.text(), zEdit.text()))

        topLayout.addStretch(1)
        topLayout.addWidget(lambdaLabel)
        topLayout.addWidget(lambdaEdit)
        topLayout.addWidget(lambdaUnitLabel)

        topLayout.addWidget(zLabel)
        topLayout.addWidget(zEdit)

        topLayout.addWidget(chanellButton)
        topLayout.addStretch(1)
        
        mainLayout = QGridLayout()

        #Add 3 rows and 1 column
        #Expand 2 rows and 1 column
        mainLayout.addLayout(topLayout,0,0,1,0)
        mainLayout.addWidget(self.midGroupBox, 1, 0)
        mainLayout.addWidget(self.bottomPlot, 2, 0)

        #Add space between boxes on rows and columns
        mainLayout.setRowStretch(1,0)
        mainLayout.setRowStretch(1,0)
        mainLayout.setColumnStretch(0,0)
        mainLayout.setColumnStretch(1,0)
        
        self.setLayout(mainLayout)

        self.setWindowTitle("mrs_chan.py")

    #Add results layout
    def createMidGroupBox(self):
        self.midGroupBox = QGroupBox("Results")

        channellLabel = QLabel("Channel:")
        channellEdit = QLineEdit('')
        channellEdit.setObjectName("canal")

        lambdaObsLabel = QLabel("λobs:")
        lambdaObsUnitLabel = QLabel("μm")
        lambdaObsEdit = QLineEdit('')
        lambdaObsEdit.setObjectName("obs")

        channellEdit.setReadOnly(True)
        lambdaObsEdit.setReadOnly(True)

        channellEdit.setContentsMargins(0, 0, 40, 0)

        layout = QHBoxLayout()
        layout.addStretch(1)
        layout.addWidget(channellLabel)
        layout.addWidget(channellEdit)

        layout.addWidget(lambdaObsLabel)
        layout.addWidget(lambdaObsEdit)
        layout.addWidget(lambdaObsUnitLabel)

        layout.addStretch(1)
        self.midGroupBox.setLayout(layout)
        

    #Create the canvas to draw the plot
    def createBottomPlot(self):
        self.bottomPlot = QGroupBox("Plot")

        self.figure = Figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)

        self.ax1 = self.figure.add_subplot(211)
        self.ax2 = self.figure.add_subplot(212)

        self.ax1.set_visible(False)
        self.ax2.set_visible(False)

        self.bottomPlot.setLayout(layout)

    #Draw the axis
    def plot(self, minL, maxL, chan, lambdaObs):
        try:
            # discards the old graph
            self.ax1.clear()
            self.ax2.clear()

            if len(chan) > 1:
                # create two axis on a canvas with 2 rows, one column and in order
                
                #Check visibility
                if not self.ax2.get_visible():
                    self.ax1.set_visible(True)
                    self.ax2.set_visible(True)

                #Axis 1
                self.ax1.set_title(chan[0])
                self.ax1.set_xlabel("Wavelength range(μm)")
                self.ax1.axvline(x=lambdaObs,color= 'r', label='λobs')

                h, labels = self.ax1.get_legend_handles_labels()
                self.ax1.legend(labels=labels, loc="upper right",
                                bbox_to_anchor=(1, 1.5))

                self.ax1.set_xlim([minL[0], maxL[0]])

                self.ax1.get_yaxis().set_visible(False)
                
                #Axis 2
                self.ax2.set_title(chan[1])
                self.ax2.set_xlabel("Wavelength range(μm)")
                self.ax2.axvline(x=lambdaObs, color= 'r',label='λobs')

                h, labels = self.ax2.get_legend_handles_labels()
                self.ax2.legend(labels=labels, loc="upper right",
                                bbox_to_anchor=(1, 1.5))

                self.ax2.set_xlim([minL[1], maxL[1]])

                self.ax2.get_yaxis().set_visible(False)
                    
            elif chan:
                
                # Create axis 1 and hide axis 2

                #Check visibility
                if not self.ax1.get_visible():
                    self.ax1.set_visible(True)

                if self.ax2.get_visible():
                    self.ax2.set_visible(False)

                self.ax1.set_title(chan[0])
                self.ax1.set_xlabel("Wavelength range(μm)")
                self.ax1.axvline(x=lambdaObs, color='r', label='λobs')

                h, labels = self.ax1.get_legend_handles_labels()
                self.ax1.legend(labels=labels, loc="center left"
                , bbox_to_anchor=(0.8, 1.2))

                self.ax1.set_xlim([minL[0], maxL[0]])

                self.ax1.get_yaxis().set_visible(False)

                self.ax2.set_visible(False)
                

            self.figure.tight_layout(pad=1)

            self.canvas.draw()
        except:
            print("Error")

    def printResults(self, emit, z):
        chan = []
        minL = []
        maxL = []
        obs = float(emit)*(1+float(z))
        #Obtain the channel of the value and it's subbands
        #If the value is between two channels, the subbands will be on subbands C and A
        #If not obtain it calling function obtainSubBand() that obtain the subbands inside a channel
        if  4.87 <= obs <= 7.76:
            if obs >= 7.45:
                channel = "1,2"
                chan = ['1C', '2A']
                minL = [6.49, 7.45]
                maxL = [7.76, 8.90]

            else:
                channel = '1'
                chan, minL, maxL = self.obtainSubBand(obs, channel)
        elif 7.76 < obs <= 11.87:
            if obs >= 11.47:
                channel = "2,3"
                chan = ['2C', '3A']
                minL = [9.91, 11.47]
                maxL = [11.87, 13.67]
            else:
                channel = '2'
                chan, minL, maxL = self.obtainSubBand(obs, channel)
        elif 11.87 < obs <= 18.24:
            if obs >= 17.54:
                channel = "3,4"
                chan = ['3C', '4A']
                minL = [15.30, 17.54]
                maxL = [18.24, 21.10]
            else:
                channel = '3'
                chan, minL, maxL = self.obtainSubBand(obs, channel)
        elif 8.24 < obs <= 28.82:
            channel = '4'
            chan, minL, maxL = self.obtainSubBand(obs, channel)
        else:
            channel = "Valores fuera de rango"

        self.midGroupBox.findChild(QLineEdit, "canal").setText(','.join(chan))
        self.midGroupBox.findChild(QLineEdit, "obs").setText(str(obs))

        self.plot(np.array(minL),  np.array(maxL), np.array(chan), obs)

    #Return subband from same channel, min and max range values of each subband
    def obtainSubBand(self, value, channelL):
        #If channel is between a range of value, it is assigned

        #If channel is 1, check subband
        if channelL == '1':
            if 4.87 <= value <= 5.82:
                if value < 5.62:
                    return ['1A'],[4.87], [5.82]
                else:
                    return ['1A','1B'], [4.87, 5.62], [5.82, 6.73]
            elif 5.82 < value <= 6.73:
                if value < 6.49:
                    return ['1B'], [5.82], [6.73]
                else:
                    return ['1B','1C'], [5.82, 6.49], [6.73, 7.76]
            else:
                return ['1C'], [6.49],[7.76]

        #If channel is 2, check subband
        elif channelL == '2':
            if 7.45 <= value <= 8.90:
                if value < 8.61:
                    return ['2A'], [7.45], [8.90]
                else:
                    return ['2A', '2B'], [7.45, 8.61], [8.90, 10.28]
            elif 8.90 < value <=10.28:
                if value < 9.91:
                    return ['2B'], [8.61],[10.28]
                else:
                    return ['2B', '2C'], [8.61, 9.91], [10.28, 11.87]
            else:
                return ['2C'], [9.91], [11.87]

        #If channel is 2, check subband
        elif channelL == '3':
            if 11.47 <=  value <= 13.67:
                if value < 13.25:
                    return ['3A'], [11.47], [13.67]
                else:
                    return ['3A', '3B'], [11.47, 13.25], [13.67, 15.80]
            elif 13.67 < value <= 15.80:
                if value < 15.30:
                    return ['3A'], [13.67], [15.80]
                else:
                    return ['3A', '3B'], [13.67, 15.30], [15.80, 18.24]
            else:
                return ['3C'], [15.30], [18.24]

        #If channel is 4, check subband
        else:
            if 17.54 <= value <= 21.10:
                if value < 20.44:
                    return ['4A'], [17.54], [21.10]
                else:
                    return ['4A', '4B'], [17.54, 20.44], [21.10, 24.72]
            elif 20.44 < value <= 24.72:
                if value < 23.84:
                    return ['4B'],[20.44], [24.72]
                else:
                    return ['4B', '4C'], [20.44, 23.84], [24.72, 28.82]
            else:
                return ['4C'], [23.84], [28.82]

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    mrs = mrsChanell()
    mrs.show()
    sys.exit(app.exec_())




