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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QHeaderView, QMainWindow,
    QPushButton, QSizePolicy, QStatusBar, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget)

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

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.stopButton = QPushButton(self.centralwidget)
        self.stopButton.setObjectName(u"stopButton")
        self.stopButton.setEnabled(False)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stopButton.sizePolicy().hasHeightForWidth())
        self.stopButton.setSizePolicy(sizePolicy)

        self.verticalLayout_2.addWidget(self.stopButton)


        self.horizontalLayout.addLayout(self.verticalLayout_2)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.captureThrottle = QPushButton(self.centralwidget)
        self.captureThrottle.setObjectName(u"captureThrottle")
        self.captureThrottle.setEnabled(False)

        self.horizontalLayout_4.addWidget(self.captureThrottle)

        self.captureBrake = QPushButton(self.centralwidget)
        self.captureBrake.setObjectName(u"captureBrake")
        self.captureBrake.setEnabled(False)

        self.horizontalLayout_4.addWidget(self.captureBrake)

        self.captureSteerRight = QPushButton(self.centralwidget)
        self.captureSteerRight.setObjectName(u"captureSteerRight")
        self.captureSteerRight.setEnabled(False)

        self.horizontalLayout_4.addWidget(self.captureSteerRight)

        self.captureSteerLeft = QPushButton(self.centralwidget)
        self.captureSteerLeft.setObjectName(u"captureSteerLeft")
        self.captureSteerLeft.setEnabled(False)

        self.horizontalLayout_4.addWidget(self.captureSteerLeft)

        self.startPipeline = QPushButton(self.centralwidget)
        self.startPipeline.setObjectName(u"startPipeline")

        self.horizontalLayout_4.addWidget(self.startPipeline)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

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
        self.stopButton.setText(QCoreApplication.translate("primaryWindow", u"Stop simulation", None))
        self.captureThrottle.setText(QCoreApplication.translate("primaryWindow", u"Record Throttle", None))
        self.captureBrake.setText(QCoreApplication.translate("primaryWindow", u"Record Brake", None))
        self.captureSteerRight.setText(QCoreApplication.translate("primaryWindow", u"Record Steer Right", None))
        self.captureSteerLeft.setText(QCoreApplication.translate("primaryWindow", u"Capture Steer Left", None))
        self.startPipeline.setText(QCoreApplication.translate("primaryWindow", u"Start Learning", None))
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

