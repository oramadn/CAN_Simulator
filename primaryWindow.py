# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'primaryWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.7.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QMainWindow, QPushButton, QSizePolicy,
    QStatusBar, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget)

class Ui_primaryWindow(object):
    def setupUi(self, primaryWindow):
        if not primaryWindow.objectName():
            primaryWindow.setObjectName(u"primaryWindow")
        primaryWindow.resize(920, 582)
        self.centralwidget = QWidget(primaryWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.startButton = QPushButton(self.centralwidget)
        self.startButton.setObjectName(u"startButton")

        self.horizontalLayout.addWidget(self.startButton)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.captureIdleButton = QPushButton(self.centralwidget)
        self.captureIdleButton.setObjectName(u"captureIdleButton")
        self.captureIdleButton.setEnabled(False)

        self.horizontalLayout_4.addWidget(self.captureIdleButton)

        self.captureThrottleButton = QPushButton(self.centralwidget)
        self.captureThrottleButton.setObjectName(u"captureThrottleButton")
        self.captureThrottleButton.setEnabled(False)

        self.horizontalLayout_4.addWidget(self.captureThrottleButton)

        self.captureBrakeButton = QPushButton(self.centralwidget)
        self.captureBrakeButton.setObjectName(u"captureBrakeButton")
        self.captureBrakeButton.setEnabled(False)

        self.horizontalLayout_4.addWidget(self.captureBrakeButton)

        self.captureSteerRightButton = QPushButton(self.centralwidget)
        self.captureSteerRightButton.setObjectName(u"captureSteerRightButton")
        self.captureSteerRightButton.setEnabled(False)

        self.horizontalLayout_4.addWidget(self.captureSteerRightButton)

        self.captureSteerLeftButton = QPushButton(self.centralwidget)
        self.captureSteerLeftButton.setObjectName(u"captureSteerLeftButton")
        self.captureSteerLeftButton.setEnabled(False)

        self.horizontalLayout_4.addWidget(self.captureSteerLeftButton)

        self.trainButton = QPushButton(self.centralwidget)
        self.trainButton.setObjectName(u"trainButton")

        self.horizontalLayout_4.addWidget(self.trainButton)

        self.loadButton = QPushButton(self.centralwidget)
        self.loadButton.setObjectName(u"loadButton")

        self.horizontalLayout_4.addWidget(self.loadButton)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.findFramesButton = QPushButton(self.centralwidget)
        self.findFramesButton.setObjectName(u"findFramesButton")

        self.horizontalLayout_3.addWidget(self.findFramesButton)

        self.throttleLabel = QLabel(self.centralwidget)
        self.throttleLabel.setObjectName(u"throttleLabel")
        self.throttleLabel.setStyleSheet(u"color: rgb(125, 40, 40);")
        self.throttleLabel.setFrameShape(QFrame.Shape.NoFrame)
        self.throttleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_3.addWidget(self.throttleLabel)

        self.brakeLabel = QLabel(self.centralwidget)
        self.brakeLabel.setObjectName(u"brakeLabel")
        self.brakeLabel.setStyleSheet(u"color: rgb(50, 78, 161)")
        self.brakeLabel.setFrameShape(QFrame.Shape.NoFrame)
        self.brakeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_3.addWidget(self.brakeLabel)

        self.steeringLabel = QLabel(self.centralwidget)
        self.steeringLabel.setObjectName(u"steeringLabel")
        self.steeringLabel.setEnabled(True)
        self.steeringLabel.setStyleSheet(u"color: rgb(90, 166, 95);")
        self.steeringLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_3.addWidget(self.steeringLabel)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.plotButton = QPushButton(self.centralwidget)
        self.plotButton.setObjectName(u"plotButton")

        self.horizontalLayout_5.addWidget(self.plotButton)


        self.verticalLayout.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.mainTable = QTableWidget(self.centralwidget)
        if (self.mainTable.columnCount() < 9):
            self.mainTable.setColumnCount(9)
        __qtablewidgetitem = QTableWidgetItem()
        self.mainTable.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.mainTable.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.mainTable.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.mainTable.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.mainTable.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.mainTable.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.mainTable.setHorizontalHeaderItem(6, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.mainTable.setHorizontalHeaderItem(7, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.mainTable.setHorizontalHeaderItem(8, __qtablewidgetitem8)
        self.mainTable.setObjectName(u"mainTable")

        self.horizontalLayout_2.addWidget(self.mainTable)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        primaryWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(primaryWindow)
        self.statusbar.setObjectName(u"statusbar")
        primaryWindow.setStatusBar(self.statusbar)

        self.retranslateUi(primaryWindow)

        QMetaObject.connectSlotsByName(primaryWindow)
    # setupUi

    def retranslateUi(self, primaryWindow):
        primaryWindow.setWindowTitle(QCoreApplication.translate("primaryWindow", u"Simulator", None))
        self.startButton.setText(QCoreApplication.translate("primaryWindow", u"Start simulation", None))
        self.captureIdleButton.setText(QCoreApplication.translate("primaryWindow", u"Record Idle", None))
        self.captureThrottleButton.setText(QCoreApplication.translate("primaryWindow", u"Record Throttle", None))
        self.captureBrakeButton.setText(QCoreApplication.translate("primaryWindow", u"Record Brake", None))
        self.captureSteerRightButton.setText(QCoreApplication.translate("primaryWindow", u"Record Steer Right", None))
        self.captureSteerLeftButton.setText(QCoreApplication.translate("primaryWindow", u"Record Steer Left", None))
        self.trainButton.setText(QCoreApplication.translate("primaryWindow", u"Train Model", None))
        self.loadButton.setText(QCoreApplication.translate("primaryWindow", u"Load Model", None))
        self.findFramesButton.setText(QCoreApplication.translate("primaryWindow", u"Find action frames", None))
        self.throttleLabel.setText(QCoreApplication.translate("primaryWindow", u"Throttle", None))
        self.brakeLabel.setText(QCoreApplication.translate("primaryWindow", u"Brake", None))
        self.steeringLabel.setText(QCoreApplication.translate("primaryWindow", u"Steering", None))
        self.plotButton.setText(QCoreApplication.translate("primaryWindow", u"Start plotting", None))
        ___qtablewidgetitem = self.mainTable.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("primaryWindow", u"ID", None));
        ___qtablewidgetitem1 = self.mainTable.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("primaryWindow", u"0", None));
        ___qtablewidgetitem2 = self.mainTable.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("primaryWindow", u"1", None));
        ___qtablewidgetitem3 = self.mainTable.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("primaryWindow", u"2", None));
        ___qtablewidgetitem4 = self.mainTable.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("primaryWindow", u"3", None));
        ___qtablewidgetitem5 = self.mainTable.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("primaryWindow", u"4", None));
        ___qtablewidgetitem6 = self.mainTable.horizontalHeaderItem(6)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("primaryWindow", u"5", None));
        ___qtablewidgetitem7 = self.mainTable.horizontalHeaderItem(7)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("primaryWindow", u"6", None));
        ___qtablewidgetitem8 = self.mainTable.horizontalHeaderItem(8)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("primaryWindow", u"7", None));
    # retranslateUi

