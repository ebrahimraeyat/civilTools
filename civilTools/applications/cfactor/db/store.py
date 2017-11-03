import sys
from PyQt4 import QtGui ,QtCore,QtSql
#from PyQt4.QtCore import Qt


class storeWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        super(storeWindow, self).__init__(parent)

        db =QtSql.QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('db.sqlite')
        if not db.open():
            QtGui.QMessageBox.critical(None,'Cannot open database',
                    "Unable to establish a database connection.\n"
                                  "This example needs SQLite support. Please read "
                                  "the Qt SQL driver documentation for information "
                                  "how to build it.\n\n"
                                  "Click Cancel to exit.",
                    QtGui.QMessageBox.Cancel)

        query = QtSql.QSqlQuery()
        QtGui.QApplication.processEvents()


        self.model = QtSql.QSqlTableModel()
        self.model.setTable('ru')
        self.model.setEditStrategy(
            QtSql.QSqlTableModel.OnManualSubmit)
        self.model.select()
        #self.model.submitAll()

        self.view = QtGui.QTableView()
        self.view.setModel(self.model)
        self.view.setSelectionBehavior(
            QtGui.QAbstractItemView.SelectRows)


        viewLayout = QtGui.QVBoxLayout()
        viewLayout.addWidget(self.view)

        self.mainVlayout = QtGui.QVBoxLayout()
        self.mainVlayout.addLayout(viewLayout)

        self.setLayout(self.mainVlayout)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    box = storeWindow()
    box.move(30,30);
    box.resize(500,500)
    box.show()
    app.exec_()