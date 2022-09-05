#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sqlite3 as lite
from PyQt5 import QtCore, QtGui, QtWidgets

class LibPopup(QtWidgets.QDialog):
    def __init__(self, libraries, lib_game, game_name, parent=None):
        super(LibPopup, self).__init__(parent=parent)

        form = QtWidgets.QFormLayout(self)
        form.addRow(QtWidgets.QLabel('Choose which category this game makes part'))
        self.listView = QtWidgets.QListView(self)
        form.addRow(self.listView)
        model = QtGui.QStandardItemModel(self.listView)
        self.setWindowTitle('%s catergories' % game_name)
        for item in libraries:
            # create an item with a caption
            standardItem = QtGui.QStandardItem(item[1])
            standardItem.setCheckable(True)
            for lib in lib_game:
                if lib[1] == item[1]:
                    standardItem.setCheckState(QtCore.Qt.Checked)
            model.appendRow(standardItem)
        self.listView.setModel(model)
        self.listView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        form.addRow(buttonBox)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def itemsSelected(self):
        selected = []
        model = self.listView.model()
        i = 0
        while model.item(i):
            if model.item(i).checkState():
                #selected.append(model.item(i).text())
                selected.append(i+1)
            i += 1
        return selected

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.showFullScreen()
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.tblGames = QtWidgets.QTableWidget(self.centralwidget)
        self.tblGames.setObjectName("tblGames")
        self.tblGames.setColumnCount(12)
        self.gridLayout.addWidget(self.tblGames, 0, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.btnOpenDb = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnOpenDb.sizePolicy().hasHeightForWidth())
        self.btnOpenDb.setSizePolicy(sizePolicy)
        self.btnOpenDb.setObjectName("btnOpenDb")
        self.horizontalLayout_2.addWidget(self.btnOpenDb)
        self.btnExit = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnExit.sizePolicy().hasHeightForWidth())
        self.btnExit.setSizePolicy(sizePolicy)
        self.btnExit.setObjectName("btnExit")
        self.horizontalLayout_2.addWidget(self.btnExit)
        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)

        self.btnOpenDb.setIcon(QtGui.QIcon.fromTheme("document-open"))
        self.btnOpenDb.clicked.connect(self.openFileNameDialog)
        self.btnExit.setIcon(QtGui.QIcon.fromTheme("application-exit"))
        self.btnExit.clicked.connect(self.quit)
        self.tblGames.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tblGames.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tblGames.verticalHeader().setVisible(False)
        self.tblGames.setHorizontalHeaderLabels(['ID', 'Game', 'Description', 'Year', 'Manufacturer', \
                                                 'Picture', 'Video', 'Last played', 'Play count', 'Rating', \
                                                 'Status', 'Library'])
        self.tblGames.itemSelectionChanged.connect(self.get_row)
        self.tblGames.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Dancade - DB Manager"))
        self.btnOpenDb.setText(_translate("MainWindow", "Open DB"))
        self.btnExit.setText(_translate("MainWindow", "Exit"))

    def openFileNameDialog(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        db_file, _ = QtWidgets.QFileDialog.getOpenFileName(MainWindow, "Select database file", "", "Sqlite3 Files (*.db3);;All Files (*)", options=options)
        if db_file:
            self.loadGames(db_file)
            self.btnOpenDb.setEnabled(False)

    def loadGames(self, db_file):
        self.db = dataBase(db_file)
        resultgame = self.db.queryGames()
        for lin in resultgame:
            # status
            status = QtWidgets.QTableWidgetItem()
            status.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            if lin[10] == 0:
                status.setCheckState(QtCore.Qt.Unchecked)
            else:
                status.setCheckState(QtCore.Qt.Checked)

            # library button
            openlib = QtWidgets.QPushButton(self.tblGames)
            openlib.setText('Libraries')
            openlib.clicked.connect(self.showLibraries)

            row = int(lin[0]) - 1
            self.tblGames.insertRow(row)
            self.tblGames.setItem(row, 0, QtWidgets.QTableWidgetItem(str(lin[0])))
            self.tblGames.setItem(row, 1, QtWidgets.QTableWidgetItem(lin[1]))
            self.tblGames.setItem(row, 2, QtWidgets.QTableWidgetItem(lin[2]))
            self.tblGames.setItem(row, 3, QtWidgets.QTableWidgetItem(lin[3]))
            self.tblGames.setItem(row, 4, QtWidgets.QTableWidgetItem(lin[4]))
            self.tblGames.setItem(row, 5, QtWidgets.QTableWidgetItem(lin[5]))
            self.tblGames.setItem(row, 6, QtWidgets.QTableWidgetItem(lin[6]))
            self.tblGames.setItem(row, 7, QtWidgets.QTableWidgetItem(lin[7]))
            self.tblGames.setItem(row, 8, QtWidgets.QTableWidgetItem(lin[8]))
            self.tblGames.setItem(row, 9, QtWidgets.QTableWidgetItem(lin[9]))
            self.tblGames.setItem(row, 10, status)
            self.tblGames.setCellWidget(row, 11, openlib)
        self.tblGames.selectRow(0)

    def get_row(self):
        selected_row = self.tblGames.selectedItems()
        self.current_row = int(selected_row[0].text())
        self.game_name = self.tblGames.item(self.current_row - 1, 1).text()

    def showLibraries(self):
        libraries = self.db.queryLibrary()
        lib_game = self.db.queryLibGame(self.current_row)
        popup = LibPopup(libraries, lib_game, self.game_name)
        if popup.exec_() == QtWidgets.QDialog.Accepted:
            for item in popup.itemsSelected():
                if lib_game:
                    if item != lib_game[0][0]:
                        sql = sql = '''INSERT INTO library (idgame, idlibname) VALUES (?, ?)'''
                        self.db.insert(sql, [self.current_row, item])
                else:
                    sql = sql = '''INSERT INTO library (idgame, idlibname) VALUES (?, ?)'''
                    self.db.insert(sql, [self.current_row, item])
        self.db.commit()

    def quit(self):
        try:
            self.db.close()
        except:
            pass
        app.quit()

# database
class dataBase():
    def __init__(self, db_file):
        try:
            self.conn = lite.connect(db_file)
        except lite.Error as e:
            print(e)
            sys.exit(1)

    def startTransaction(self):
        self.cur = self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def insert(self, sql, values):
        cur = self.conn.cursor()
        cur.execute(sql, values)

    def close(self):
        self.conn.close()

    def queryLibrary(self):
        cur_lib = self.conn.cursor()
        cur_lib.execute("SELECT * FROM libraryname")
        data_lib = cur_lib.fetchall()
        return data_lib

    def queryGames(self):
        cur_game = self.conn.cursor()
        cur_game.execute("SELECT * FROM game ORDER BY 'description'")
        data_game = cur_game.fetchall()
        return data_game

    def queryLibGame(self, game):
        cur_game = self.conn.cursor()
        cur_game.execute('''SELECT libraryname.id, libraryname.name
                            FROM game
                                INNER JOIN library
                                    ON game.id = library.idgame
                                INNER JOIN libraryname
                                    ON library.idlibname = libraryname.id
                            WHERE library.idgame = %d
                            ORDER BY library.id''' % game)
        data_game = cur_game.fetchall()
        return data_game

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
