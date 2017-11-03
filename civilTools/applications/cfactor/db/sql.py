# -*- coding: utf-8 -*-

from PyQt4 import QtSql, QtGui
import csv
import codecs
CODEC = "UTF-8"
data = []

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
query.exec_('''CREATE TABLE  rufactor(
noeSystem TEXT NOT NULL,
noeLateral TEXT PRIMARY KEY UNIQUE NOT NULL,
Ru TEXT NOT NULL,
phi0 TEXT NOT NULL,
cd TEXT NOT NULL,
H TEXT,
alpha TEXT NOT NULL,
pow TEXT NOT NULL,
infill TEXT,
ID TEXT NOT NULL
)''')


def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]


def csvtosqlite(fname):

    with open(unicode(fname), 'rb') as stream:
        for rowdata in unicode_csv_reader(stream):
            if rowdata[0] == 'comment':
                continue
            if rowdata[0] == 'title':
                data.append(rowdata[1])
                continue
            else:
                for i in range(len(rowdata)):
                    data.append(rowdata[i])
                setData(data)


def setData(data):
    query = QtSql.QSqlQuery()
    query.exec_(
        """INSERT INTO rufactor(ID) VALUES ("%s")""" % (data[9]))


csvtosqlite("Ru.csv")