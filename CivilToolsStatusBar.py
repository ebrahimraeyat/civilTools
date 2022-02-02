

import os
import FreeCAD
from CivilToolsTranslateUtils import *


# Language path for InitGui.py


def getLanguagePath():

    return os.path.join(os.path.dirname(__file__),"translations")


# Status bar buttons


def setStatusIcons(show=True):

    "shows or hides the BIM icons in the status bar"

    import FreeCADGui
    from PySide import QtCore,QtGui
    import etabs_obj

    force_units = [ 'kgf', 'N', 'kN', 'tonf']
    length_units = ['m', 'cm', 'mm']

    def set_unit(action):
        utext = action.text().replace("&","")
        # unit = [0,4,1,3,7,5][unitsList.index(utext)]
        action.parent().parent().parent().setText(utext)
        etabs = etabs_obj.EtabsModel(backup=False)
        if etabs.success:
            mw = FreeCADGui.getMainWindow()
            statuswidget = mw.findChild(QtGui.QToolBar,"CivilToolsStatusWidget")
            force = statuswidget.force_label.text()
            length = statuswidget.length_label.text()
            print(force, length)
            print('changed')
            etabs.set_current_unit(force, length)


    def addonMgr():

        mw = FreeCADGui.getMainWindow()
        if mw:
            st = mw.statusBar()
            statuswidget = st.findChild(QtGui.QToolBar,"CivilToolsStatusWidget")
            if statuswidget:
                updatebutton = statuswidget.findChild(QtGui.QPushButton,"UpdateButton")
                if updatebutton:
                    statuswidget.actions()[-1].setVisible(False)
        FreeCADGui.runCommand("Std_AddonMgr")

    
    class CheckWorker(QtCore.QThread):

        updateAvailable = QtCore.Signal(bool)

        def __init__(self):

            QtCore.QThread.__init__(self)

        def run(self):

            try:
                import git
            except ImportError:
                return
            FreeCAD.Console.PrintLog("Checking for available updates of the civilTools workbench\n")
            civiltools_dir = os.path.join(FreeCAD.getUserAppDataDir(),"Mod","civilTools")
            etabs_api_dir = os.path.join(FreeCAD.getUserAppDataDir(),"Mod","etabs_api")
            for directory in (civiltools_dir, etabs_api_dir):
                if os.path.exists(directory) and os.path.exists(directory + os.sep + '.git'):
                    gitrepo = git.Git(directory)
                    try:
                        gitrepo.fetch()
                        if "git pull" in gitrepo.status():
                            self.updateAvailable.emit(True)
                            return
                    except:
                        # can fail for any number of reasons, ex. not being online
                        pass
            self.updateAvailable.emit(False)

    def checkUpdates():
        FreeCAD.civiltools_update_checker = CheckWorker()
        FreeCAD.civiltools_update_checker.updateAvailable.connect(showUpdateButton)
        FreeCAD.civiltools_update_checker.start()

    def showUpdateButton(avail):
        if avail:
            FreeCAD.Console.PrintLog("A civilTools update is available\n")
            mw = FreeCADGui.getMainWindow()
            if mw:
                st = mw.statusBar()
                statuswidget = st.findChild(QtGui.QToolBar,"CivilToolsStatusWidget")
                if statuswidget:
                    updatebutton = statuswidget.findChild(QtGui.QPushButton,"UpdateButton")
                    if updatebutton:
                        # updatebutton.show() # doesn't work for some reason
                        statuswidget.actions()[-1].setVisible(True)
        else:
            FreeCAD.Console.PrintLog("No civilTools update available\n")
        if hasattr(FreeCAD,"civiltools_update_checker"):
            del FreeCAD.civiltools_update_checker


    # main code

    mw = FreeCADGui.getMainWindow()
    if mw:
        st = mw.statusBar()
        statuswidget = st.findChild(QtGui.QToolBar,"CivilToolsStatusWidget")
        if show:
            if statuswidget:
                statuswidget.show()
            else:
                statuswidget = QtGui.QToolBar()
                statuswidget.setObjectName("CivilToolsStatusWidget")
                # force menue
                force_label = QtGui.QPushButton("force")
                force_label.setObjectName("force_label")
                force_label.setFlat(True)
                menu = QtGui.QMenu(force_label)
                g_force_units = QtGui.QActionGroup(menu)
                for u in force_units:
                    a = QtGui.QAction(g_force_units)
                    a.setText(u)
                    menu.addAction(a)
                force_label.setMenu(menu)
                g_force_units.triggered.connect(set_unit)
                etabs = etabs_obj.EtabsModel(backup=False)
                force, length = 'kgf', 'm'
                if etabs.success:
                    force, length = etabs.get_current_unit()
                force_label.setText(force)
                force_label.setToolTip(translate("civiltools","The preferred force unit"))
                statuswidget.addWidget(force_label)
                statuswidget.force_label = force_label
                st.addPermanentWidget(statuswidget)
                # length menue
                length_label = QtGui.QPushButton("force")
                length_label.setObjectName("length_label")
                length_label.setFlat(True)
                menu = QtGui.QMenu(length_label)
                g_length_units = QtGui.QActionGroup(menu)
                for u in length_units:
                    a = QtGui.QAction(g_length_units)
                    a.setText(u)
                    menu.addAction(a)
                length_label.setMenu(menu)
                g_length_units.triggered.connect(set_unit)
                etabs = etabs_obj.EtabsModel(backup=False)
                length_label.setText(length)
                length_label.setToolTip(translate("civiltools","The preferred length unit"))
                statuswidget.addWidget(length_label)
                statuswidget.length_label = length_label

                # update notifier button (starts hidden)
                updatebutton = QtGui.QPushButton()
                bwidth = updatebutton.fontMetrics().boundingRect("AAAA").width()
                updatebutton.setObjectName("UpdateButton")
                updatebutton.setMaximumWidth(bwidth)
                updatebutton.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),"images","update.png")))
                updatebutton.setText("")
                updatebutton.setToolTip(translate("civilTools","An update to the civilTools workbench is available. Click here to open the addons manager."))
                updatebutton.setFlat(True)
                QtCore.QObject.connect(updatebutton,QtCore.SIGNAL("pressed()"),addonMgr)
                updatebutton.hide()
                statuswidget.addWidget(updatebutton)
                QtCore.QTimer.singleShot(2500, checkUpdates) # delay a bit the check for civilTools WB update...
        else:
            if statuswidget:
                statuswidget.hide()
            else:
                # when switching workbenches, the toolbar sometimes "jumps"
                # out of the status bar to any other dock area...
                statuswidget = mw.findChild(QtGui.QToolBar,"CivilToolsStatusWidget")
                if statuswidget:
                    statuswidget.hide()

