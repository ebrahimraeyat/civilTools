# -*- coding: utf-8 -*-
#===================================================================
# Module with functions to save & restore qt widget values
# Written by: Alan Lilly
# Website: http://panofish.net
#===================================================================
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import inspect

#===================================================================
# save "ui" controls and values to registry "setting"
# currently only handles comboboxes editlines & checkboxes
# ui = qmainwindow object
# settings = qsettings object
#===================================================================


def guisave(ui, settings):

    #for child in ui.children():  # works like getmembers, but because it traverses the hierarachy,
    #you would have to call guisave recursively to traverse down the tree

    for name, obj in inspect.getmembers(ui):
        #if type(obj) is QComboBox:  # this works similar to isinstance, but missed some field... not sure why?
        if isinstance(obj, QComboBox):
            name = obj.objectName()
            if not name:
                continue
            index = obj.currentIndex()
            #text   = obj.itemText(index)   # get the text for current index
            settings.setValue(name, index)   # save combobox selection to registry

        if isinstance(obj, QLineEdit):
            name = obj.objectName()
            value = obj.text()
            settings.setValue(name, value)    # save ui values, so they can be restored next time

        if isinstance(obj, QCheckBox):
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
            #index  = obj.currentIndex()    # get current region from combobox
            #text   = obj.itemText(index)   # get the text for new selected index
            name = obj.objectName()
            if not name:
                continue
            index = settings.value(name).toInt()[0]

            #value = unicode(settings.value(name).toString())

            #if value == "":
                #continue

            #index = obj.findText(value)   # get the corresponding index for specified string in combobox

            #if index == -1:  # add to list if not found
                #obj.insertItems(0,[value])
                #index = obj.findText(value)
                #obj.setCurrentIndex(index)
            #else:
            obj.setCurrentIndex(index)   # preselect a combobox value by index

        if isinstance(obj, QLineEdit):
            name = obj.objectName()
            value = unicode(settings.value(name).toString())  # get stored value from registry
            obj.setText(value)  # restore lineEditFile

        #if isinstance(obj, QCheckBox):
            #name = obj.objectName()
            #value = settings.value(name).toString()   # get stored value from registry
            #if value != None:
                #obj.setCheckState(value)   # restore checkbox

        #if isinstance(obj, QRadioButton):


 #Very useful little module. Thanks! It works nicely when saving QSettings to an ini file, e.g.
 #guisave(self.ui, QtCore.QSettings('saved.ini', QtCore.QSettings.IniFormat)) which creates a
 #file that can be shared between users. – Snorfalorpagus Oct 3 '14 at 8:59

#I had to change a couple of lines to value = unicode(settings.value(name).toString())
#as settings.value was returning a QVariant. – Snorfalorpagus Oct 3 '14 at 9:16

#Just noticed that the use of obj.setCheckState(value) for QCheckBox objects enables tristate,
#which may not be desired. In my case I know I never wanted tristate I used obj.setChecked(value)
#instead. I'm not sure how to detect this on load, and restore correctly for both cases.

#s = QVariant(QString.number(2., 'f', 2))