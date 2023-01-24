# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QMainWindow, QMenu, QMenuBar,
    QSizePolicy, QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.actionSave_data = QAction(MainWindow)
        self.actionSave_data.setObjectName(u"actionSave_data")
        self.actionLoad_data = QAction(MainWindow)
        self.actionLoad_data.setObjectName(u"actionLoad_data")
        self.actionPNG = QAction(MainWindow)
        self.actionPNG.setObjectName(u"actionPNG")
        self.actionPrinter = QAction(MainWindow)
        self.actionPrinter.setObjectName(u"actionPrinter")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuExport = QMenu(self.menuFile)
        self.menuExport.setObjectName(u"menuExport")
        self.menuSettings = QMenu(self.menubar)
        self.menuSettings.setObjectName(u"menuSettings")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menuFile.addAction(self.actionSave_data)
        self.menuFile.addAction(self.actionLoad_data)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.menuExport.menuAction())
        self.menuExport.addAction(self.actionPNG)
        self.menuSettings.addAction(self.actionPrinter)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionSave_data.setText(QCoreApplication.translate("MainWindow", u"Save data", None))
        self.actionLoad_data.setText(QCoreApplication.translate("MainWindow", u"Load data", None))
        self.actionPNG.setText(QCoreApplication.translate("MainWindow", u"PNG", None))
        self.actionPrinter.setText(QCoreApplication.translate("MainWindow", u"Printer", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuExport.setTitle(QCoreApplication.translate("MainWindow", u"Export", None))
        self.menuSettings.setTitle(QCoreApplication.translate("MainWindow", u"Settings", None))
    # retranslateUi

