# Form implementation generated from reading ui file 'test_ui.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_LogercollectorJAMES(object):
    def setupUi(self, LogercollectorJAMES):
        LogercollectorJAMES.setObjectName("LogercollectorJAMES")
        LogercollectorJAMES.resize(385, 250)
        self.centralwidget = QtWidgets.QWidget(LogercollectorJAMES)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(200, 170, 75, 23))
        self.pushButton.setStyleSheet("QPushButton{\n"
"    background-color: white;\n"
"    width: 75px;\n"
"    height: 25px;\n"
"    font-size: 12px;\n"
"    border: none;\n"
"    text-align: center;\n"
"}\n"
"QPushButton:hover{\n"
"background-color: silver;\n"
"}\n"
"QPushButton:pressed{\n"
"background-color: grey;\n"
"}")
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(90, 170, 75, 23))
        self.pushButton_2.setStyleSheet("QPushButton{\n"
"    background-color: white;\n"
"    width: 75px;\n"
"    height: 25px;\n"
"    font-size: 12px;\n"
"    border: none;\n"
"    text-align: center;\n"
"}\n"
"QPushButton:hover{\n"
"background-color: silver;\n"
"}\n"
"QPushButton:pressed{\n"
"background-color: grey;\n"
"}")
        self.pushButton_2.setObjectName("pushButton_2")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(40, 10, 311, 121))
        self.textBrowser.setObjectName("textBrowser")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(10, 170, 41, 41))
        self.frame.setStyleSheet("image: url(logo.png);")
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame.setObjectName("frame")
        LogercollectorJAMES.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(LogercollectorJAMES)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 385, 21))
        self.menubar.setObjectName("menubar")
        LogercollectorJAMES.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(LogercollectorJAMES)
        self.statusbar.setObjectName("statusbar")
        LogercollectorJAMES.setStatusBar(self.statusbar)

        self.retranslateUi(LogercollectorJAMES)
        QtCore.QMetaObject.connectSlotsByName(LogercollectorJAMES)

    def retranslateUi(self, LogercollectorJAMES):
        _translate = QtCore.QCoreApplication.translate
        LogercollectorJAMES.setWindowTitle(_translate("LogercollectorJAMES", "Loger - JAMES"))
        self.pushButton.setText(_translate("LogercollectorJAMES", "collect"))
        self.pushButton_2.setText(_translate("LogercollectorJAMES", "exit"))


