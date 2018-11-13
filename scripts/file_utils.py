# -*- coding: utf-8 -*-
"""
Program:
    File Utils
    (LibreEngineering)
    file_utils.py

Author:
    Alex Borisov <>

Copyright (c) 2010-2012 Alex Borisov

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from PyQt5 import QtCore, QtGui, QtWidgets

def make_data_backup(file_name):
    data_file_info = QtCore.QFileInfo(file_name)
    data_file_dir = data_file_info.absolutePath()
    data_file_base = data_file_info.completeBaseName()
    data_file_ext = data_file_info.completeSuffix()
    backup_file_ext = data_file_info.completeSuffix() + "~"
    data_file_name = data_file_dir + "/" + data_file_base + "." + data_file_ext
    backup_file_name = data_file_dir + "/" + data_file_base + "." + backup_file_ext
    data_file = QtCore.QFile(data_file_name)
    backup_file = QtCore.QFile(backup_file_name)

    if data_file.exists():
        if backup_file.exists():
            backup_file.remove()
            data_file.copy(backup_file_name)
            return True
        else:
            data_file.copy(backup_file_name)
            return True
    else:
        return False

def find_data_file(file_name):
    f = QtCore.QFile(file_name)
    if f.exists():
        return True
    else:
        return False

def select_data_file(parent, s, title, path):
    dlg_title = "Select " + s + " data file - " + title
    dlg_filter = "SQLite database files (*.sqlite)"
    file_dir = QtCore.QDir(path)
    file_name = QtGui.QFileDialog.getOpenFileName(parent, dlg_title, file_dir.absolutePath(), dlg_filter)
    file_info = QtCore.QFileInfo(file_name)
    if file_info.isFile():
        return file_name
    else:
        return None

def check_file_input(file_name):
    if file_name == "" or not QtCore.QFile(file_name).exists():
        return False
    else:
        return True

def check_dir_input(dir_name):
    if dir_name == "" or not QtCore.QDir(dir_name).exists():
        return False
    else:
        return True

def delete_file(file_name):
    if QtCore.QFile(file_name).exists():
        QtCore.QFile(file_name).remove()
        return True
    else:
        return False

def overwrite_file_dlg(parent, title):
    dlg = QtGui.QMessageBox(parent)
    dlg.setIcon(QtGui.QMessageBox.Question)
    dlg.setWindowTitle("File exists - " + title)
    dlg.setText("Overwrite existing file?")
    dlg.addButton(QtGui.QMessageBox.Yes)
    dlg.addButton(QtGui.QMessageBox.No)
    dlg.setDefaultButton(QtGui.QMessageBox.No)
    button = dlg.exec_()
    if (button == QtGui.QMessageBox.Yes):
        return True
    else:
        return False
