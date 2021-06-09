from PyQt5 import QtCore, QtGui, QtWidgets
import time
from PyQt5.QtCore import pyqtSignal
from showa.modules import writeRead, GV


class QThread1(QtCore.QThread):
    sig1 = pyqtSignal(list)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

    def zoom(self, items):
        self.source_txt = items

    def run(self):
        sercomlist = self.source_txt
        try:
            # print(sercomlist)
            # print(sercomlist[0], sercomlist[1])
            # time.sleep(2)
            GV.main(sercomlist[0], sercomlist[1])
        except Exception as e:
            print(e)
        finally:
            self.sig1.emit(self.source_txt)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(631, 434)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.generate_btn = QtWidgets.QPushButton(self.centralwidget)
        self.generate_btn.setGeometry(QtCore.QRect(130, 220, 371, 61))
        self.generate_btn.setObjectName("generate_btn")
        self.com_lbl = QtWidgets.QLabel(self.centralwidget)
        self.com_lbl.setGeometry(QtCore.QRect(130, 30, 150, 16))
        self.com_lbl.setObjectName("com_lbl")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(400, 310, 111, 16))
        self.label_3.setObjectName("label_3")
        self.connect_btn = QtWidgets.QPushButton(self.centralwidget)
        self.connect_btn.setGeometry(QtCore.QRect(130, 50, 371, 61))
        self.connect_btn.setObjectName("connect_btn")
        self.serial_no = QtWidgets.QLineEdit(self.centralwidget)
        self.serial_no.setGeometry(QtCore.QRect(130, 160, 371, 31))
        self.serial_no.setObjectName("serial_no")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(130, 310, 261, 21))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(130, 140, 241, 16))
        self.label.setMaximumSize(QtCore.QSize(1000, 20))
        self.label.setObjectName("label")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 631, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.generate_btn.setEnabled(False)
        self.serial_no.setEnabled(False)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow",
                                             "GV Cylinder Torque Collection"))
        self.generate_btn.setText(_translate("MainWindow", "GENERATE"))
        self.com_lbl.setText(_translate("MainWindow", "Click connect"))
        self.label_3.setText(_translate("MainWindow", "Click Generate"))
        self.connect_btn.setText(_translate("MainWindow", "CONNECT"))
        self.label.setText(_translate("MainWindow",
                                      "Key in GV cylinder serial number"))


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    sig = pyqtSignal(list)

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        # print(bool(self.serial_no.text()))
        self.connect_btn.clicked.connect(self.onConnect)
        self.serial_no.textChanged.connect(self.on_text_changed)
        self.generate_btn.clicked.connect(self.onGenerate)
        self.serial_no.editingFinished.connect(self.checkstatus)

    def checkstatus(self):
        if self.serial_no.text() == "":
            pass
        else:
            self.generate_btn.setEnabled(True)

    @QtCore.pyqtSlot()
    def on_text_changed(self):
        self.generate_btn.setEnabled(bool(self.serial_no.text()) and
                                     self.com_lbl.text() != "Click connect" and
                                     self.com_lbl.text() != "Not connected. Try again")

    def onConnect(self):
        try:
            if writeRead.getCOM():
                self.com_lbl.setText(writeRead.getCOM())
                self.connect_btn.setEnabled(False)
                self.serial_no.setEnabled(True)
            else:
                pass
        except Exception as e:
            self.com_lbl.setText("Not connected. Try again")
            print(e)

    def onGenerate(self):
        serial_num = self.serial_no.text()
        commie = self.com_lbl.text()
        items = [serial_num, commie]
        self.progressBar.setRange(0, 0)
        self.label_3.setText(f"collecting data..")
        self.thread1 = QThread1()
        self.sig.connect(self.thread1.zoom)
        self.sig.emit(items)
        self.thread1.start()
        # # time.sleep(2)
        self.generate_btn.setEnabled(False)
        self.serial_no.setEnabled(False)
        self.thread1.sig1.connect(self.done)

    def done(self, info):
        self.progressBar.setRange(0, 1)
        self.progressBar.setValue(1)
        self.label_3.setText("Done!")
        try:
            self.thread1.running = False
            time.sleep(1)
            self.connect_btn.setEnabled(True)
        except Exception as error:
            print(error)
            pass


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
