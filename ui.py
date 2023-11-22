# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QPushButton, QSizePolicy, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(454, 347)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.layoutWidget = QWidget(self.centralwidget)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(30, 60, 397, 33))
        self.horizontalLayout = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.accountLabel = QLabel(self.layoutWidget)
        self.accountLabel.setObjectName(u"accountLabel")

        self.horizontalLayout.addWidget(self.accountLabel)

        self.accountInput = QLineEdit(self.layoutWidget)
        self.accountInput.setObjectName(u"accountInput")

        self.horizontalLayout.addWidget(self.accountInput)

        self.passwordLabel = QLabel(self.layoutWidget)
        self.passwordLabel.setObjectName(u"passwordLabel")

        self.horizontalLayout.addWidget(self.passwordLabel)

        self.passwordInput = QLineEdit(self.layoutWidget)
        self.passwordInput.setObjectName(u"passwordInput")
        self.passwordInput.setEchoMode(QLineEdit.Password)

        self.horizontalLayout.addWidget(self.passwordInput)

        self.loginButton = QPushButton(self.layoutWidget)
        self.loginButton.setObjectName(u"loginButton")

        self.horizontalLayout.addWidget(self.loginButton)

        self.title = QLabel(self.centralwidget)
        self.title.setObjectName(u"title")
        self.title.setGeometry(QRect(110, 10, 241, 41))
        font = QFont()
        font.setPointSize(24)
        self.title.setFont(font)
        self.outputMsg = QTextEdit(self.centralwidget)
        self.outputMsg.setObjectName(u"outputMsg")
        self.outputMsg.setGeometry(QRect(30, 260, 331, 51))
        self.outputMsg.setReadOnly(True)
        self.website = QLabel(self.centralwidget)
        self.website.setObjectName(u"website")
        self.website.setGeometry(QRect(200, 320, 71, 16))
        font1 = QFont()
        font1.setPointSize(8)
        self.website.setFont(font1)
        self.website.setAlignment(Qt.AlignCenter)
        self.courseList = QTextEdit(self.centralwidget)
        self.courseList.setObjectName(u"courseList")
        self.courseList.setGeometry(QRect(30, 103, 331, 141))
        self.courseList.setReadOnly(True)
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(370, 210, 59, 100))
        self.verticalLayout = QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.aboutButton = QPushButton(self.widget)
        self.aboutButton.setObjectName(u"aboutButton")

        self.verticalLayout.addWidget(self.aboutButton)

        self.settingsButton = QPushButton(self.widget)
        self.settingsButton.setObjectName(u"settingsButton")

        self.verticalLayout.addWidget(self.settingsButton)

        self.exitButton = QPushButton(self.widget)
        self.exitButton.setObjectName(u"exitButton")

        self.verticalLayout.addWidget(self.exitButton)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Zuvio \u81ea\u52d5\u9ede\u540d\u5c0f\u5e6b\u624b @mlgzackfly", None))
        self.accountLabel.setText(QCoreApplication.translate("MainWindow", u"\u5b78\u865f", None))
        self.passwordLabel.setText(QCoreApplication.translate("MainWindow", u"\u5bc6\u78bc", None))
        self.passwordInput.setInputMask("")
        self.loginButton.setText(QCoreApplication.translate("MainWindow", u"\u555f\u52d5", None))
        self.title.setText(QCoreApplication.translate("MainWindow", u"Zuvio \u81ea\u52d5\u9ede\u540d\u5c0f\u5e6b\u624b", None))
        self.website.setText(QCoreApplication.translate("MainWindow", u"mlgzackfly.com", None))
        self.aboutButton.setText(QCoreApplication.translate("MainWindow", u"\u95dc\u65bc", None))
        self.settingsButton.setText(QCoreApplication.translate("MainWindow", u"\u8a2d\u5b9a", None))
        self.exitButton.setText(QCoreApplication.translate("MainWindow", u"\u96e2\u958b", None))
    # retranslateUi

