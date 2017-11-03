# -*- coding: utf-8 -*-
#===================================================================
# Module with functions to save & restore qt widget values
# Written by: Alan Lilly
# Website: http://panofish.net
#===================================================================

import sys
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import inspect

#===================================================================
# save "ui" controls and values to registry "setting"
# currently only handles comboboxes editlines & checkboxes
# ui = qmainwindow object
# settings = qsettings object
#===================================================================

def guisave(ui, settings):

    #for child in ui.children():  # works like getmembers, but because it traverses the hierarachy, you would have to call guisave recursively to traverse down the tree

    for name, obj in inspect.getmembers(ui):
        #if type(obj) is QComboBox:  # this works similar to isinstance, but missed some field... not sure why?
        if isinstance(obj, QComboBox):
            print 'Qcombobox'
            name   = obj.objectName()      # get combobox name
            index  = obj.currentIndex()    # get current index from combobox
            text   = obj.itemText(index)   # get the text for current index
            settings.setValue(name, text)   # save combobox selection to registry
            print '{} index and value is: {}, {}'.format(name, index, text)

        if isinstance(obj, QLineEdit):
            name = obj.objectName()
            value = obj.text()
            print 'name is:{}'.format(name)
            print 'value is: {}'.format(value)
            settings.setValue(name, value)    # save ui values, so they can be restored next time

        if isinstance(obj, QCheckBox):
            print 'Qcheckbox'
            name = obj.objectName()
            state = obj.checkState()
            settings.setValue(name, state)

#===================================================================
# restore "ui" controls with values stored in registry "settings"
# currently only handles comboboxes, editlines &checkboxes
# ui = QMainWindow object
# settings = QSettings object
#===================================================================

def guirestore(ui, settings):

    for name, obj in inspect.getmembers(ui):
        if isinstance(obj, QComboBox):
            index  = obj.currentIndex()    # get current region from combobox
            #text   = obj.itemText(index)   # get the text for new selected index
            name   = obj.objectName()


            value = unicode(settings.value(name).toString())
            print '{} index and value is: {}, {}'.format(name, index, value)

            if value == "":
                continue

            index = obj.findText(value)   # get the corresponding index for specified string in combobox

            if index == -1:  # add to list if not found
                obj.insertItems(0,[value])
                index = obj.findText(value)
                obj.setCurrentIndex(index)
            else:
                obj.setCurrentIndex(index)   # preselect a combobox value by index


        if isinstance(obj, QLineEdit):
            name = obj.objectName()
            value = unicode(settings.value(name).toString())  # get stored value from registry
            obj.setText(value)  # restore lineEditFile

        if isinstance(obj, QCheckBox):
            name = obj.objectName()
            value = settings.value(name).toString()   # get stored value from registry
            if value != None:
                obj.setCheckState(value)   # restore checkbox

        #if isinstance(obj, QRadioButton):

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle('PyQtConfig Demo')
        gd = QGridLayout()

        self.sb = QSpinBox()
        gd.addWidget(self.sb, 0, 1)

        self.te = QLineEdit()
        self.te.setObjectName('lineEdit')
        gd.addWidget(self.te, 1, 1)

        cb = QCheckBox()
        gd.addWidget(cb, 2, 1)

        self.cmb = QComboBox()
        self.cmb.setObjectName('cmbBox')
        self.cmb.addItems(['ali', 'ebi', 'kobi'])
        gd.addWidget(self.cmb, 3, 1)

        self.current_config_output = QTextEdit()
        gd.addWidget(self.current_config_output, 0, 3, 3, 1)


        self.window = QWidget()
        self.window.setLayout(gd)
        self.setCentralWidget(self.window)
        programname = os.path.basename(__file__)
        programbase, ext = os.path.splitext(programname)
        settings = QSettings("company", programbase)
        guirestore(self, settings)


    def closeEvent(self, event):
        programname = os.path.basename(__file__)
        programbase, ext = os.path.splitext(programname)
        settings = QSettings("company", programbase)
        guisave(self, settings)
        self.deleteLater()


################################################################

if __name__ == "__main__":

    # execute when run directly, but not when called as a module.
    # therefore this section allows for testing this module!

    #print "running directly, not as a module!"


    # Create a Qt application
    app = QApplication(sys.argv)
    w = MainWindow()
    for name, obj in inspect.getmembers(w):
        try:
            print obj.objectName()
        except: pass
    w.show()
    app.exec_()  # Enter Qt application main loop


 #Very useful little module. Thanks! It works nicely when saving QSettings to an ini file, e.g. guisave(self.ui, QtCore.QSettings('saved.ini', QtCore.QSettings.IniFormat)) which creates a file that can be shared between users. – Snorfalorpagus Oct 3 '14 at 8:59
   	 #
	#
#I had to change a couple of lines to value = unicode(settings.value(name).toString()) as settings.value was returning a QVariant. – Snorfalorpagus Oct 3 '14 at 9:16
   	 #
	#
#Cool improvements Snorfalorpagus! Me likey :) – panofish Oct 3 '14 at 13:22
   	 #
	#
#Just noticed that the use of obj.setCheckState(value) for QCheckBox objects enables tristate, which may not be desired. In my case I know I never wanted tristate I used obj.setChecked(value) instead. I'm not sure how to detect this on load, and restore correctly for both cases. – Snorfalorpagus Nov 17 '14 at 16:17