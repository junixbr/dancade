#!/usr/bin/python3
# -*- coding: utf-8 -*-

####
# Project Dancade
# A Mame frontend.
#
# Copyright © 2022 Dancade Project Team
####

from PyQt5.QtCore import Qt, QCoreApplication, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFormLayout, QProgressBar
from PyQt5.QtGui import QIcon, QPixmap, QFont, QFontDatabase
import sys

#from lib import settings
from lib import utils
from lib import db

# settings
global CONFS
CONFS=[]
#CONFS = settings.readConf()
CONFS.append('resources/mame/roms')

class mainUI(QMainWindow):
    def __init__(self):
        super(mainUI, self).__init__()
        self.setStyleSheet("background-image: url(../resources/img/background.png);")

        # progress bar
        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(860, 662, 200, 20)

        # custom label
        self.cwidget = QWidget()

        # custom truetype font
        id = QFontDatabase.addApplicationFont('../resources/font/cronusround.otf')
        self.families = QFontDatabase.applicationFontFamilies(id)

        self.showFullScreen()
        self.setCursor(Qt.BlankCursor)

    def drawBar(self, value):
        self.pbar.setValue(value)

def main():
    app = QApplication(sys.argv)
    window = mainUI()
    utils.utilsMain(window)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()