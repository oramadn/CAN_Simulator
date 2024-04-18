# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'inputWindow.ui'
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
from PySide6.QtWidgets import (QApplication, QMainWindow, QMenuBar, QSizePolicy,
    QStatusBar, QWidget)

class Ui_inputWindow(object):
    def setupUi(self, inputWindow):
        if not inputWindow.objectName():
            inputWindow.setObjectName(u"inputWindow")
        inputWindow.resize(800, 600)
        self.centralwidget = QWidget(inputWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        inputWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(inputWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 33))
        inputWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(inputWindow)
        self.statusbar.setObjectName(u"statusbar")
        inputWindow.setStatusBar(self.statusbar)

        self.retranslateUi(inputWindow)

        QMetaObject.connectSlotsByName(inputWindow)
    # setupUi

    def retranslateUi(self, inputWindow):
        inputWindow.setWindowTitle(QCoreApplication.translate("inputWindow", u"MainWindow", None))
    # retranslateUi

