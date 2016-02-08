# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore, QtSql

DATABASE_NAME = "db.sqlite"
class storeWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        super(storeWindow, self).__init__(parent)

        db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName(DATABASE_NAME)
        if not db.open():
            QtGui.QMessageBox.critical(None,'Cannot open database',
                    "Unable to establish a database connection.\n"
                                  "This example needs SQLite support. Please read "
                                  "the Qt SQL driver documentation for information "
                                  "how to build it.\n\n"
                                  "Click Cancel to exit.",
                    QtGui.QMessageBox.Cancel)

        #QtGui.QApplication.processEvents()
        dbHeaders = (u'سیستم سازه', u'سیستم مقاوم در برابر نیروی جانبی',
                'Ru', u'\u2126 0', 'Cd', 'H (m)','alpha','pow','infill','ID')
        #columnWidth = (120, 300)

        self.model = QtSql.QSqlTableModel()
        self.model.setTable('ru')
        #self.model.setEditStrategy(
            #QtSql.QSqlTableModel.OnManualSubmit)
        self.model.select()

        for i, head in enumerate(dbHeaders):
            self.model.setHeaderData(i, QtCore.Qt.Horizontal, head)

        #
        # table view
        #

        font = QtGui.QFont()
        font.setFamily("Tahoma")
        #font.setBold(True)
        font.setPointSize(9)

        self.view = QtGui.QTableView()
        self.view.setFont(font)
        self.view.setModel(self.model)
        self.view.setSelectionBehavior(
            QtGui.QAbstractItemView.SelectRows)

        headerAlign = QtGui.QHeaderView(QtCore.Qt.Horizontal)
        headerAlign.setDefaultAlignment(QtCore.Qt.AlignCenter)
        self.view.setHorizontalHeader(headerAlign)
        self.view.resizeColumnsToContents()
        self.view.setAlternatingRowColors(True)
        #self.view.setStyleSheet(
            #"alternate-background-color: yellow;background-color: blue;")
        self.view.setSpan(0, 0, 5, 1)
        self.view.setSpan(5, 0, 7, 1)
        self.view.setSpan(12, 0, 6, 1)
        self.view.setSpan(18, 0, 8, 1)
        #for i in (6, 7, 8, 9):
            #self.view.hideColumn(i)


        self.viewLayout = QtGui.QVBoxLayout()
        self.viewLayout.addWidget(self.view)

        mainVlayout = QtGui.QVBoxLayout()
        mainVlayout.addLayout(self.viewLayout)

        self.setLayout(mainVlayout)



if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    box = storeWindow()
    box.move(30,30);
    box.resize(500,500)
    box.show()
    app.exec_()