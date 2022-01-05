

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
                if os.path.exists(directory):
                    if os.path.exists(directory + os.sep + '.git'):
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
                        #updatebutton.show() # doesn't work for some reason
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

                # update notifier button (starts hidden)
                updatebutton = QtGui.QPushButton()
                bwidth = updatebutton.fontMetrics().boundingRect("AAAA").width()
                updatebutton.setObjectName("UpdateButton")
                updatebutton.setMaximumWidth(bwidth)
                updatebutton.setIcon(QtGui.QIcon(":/images/update.png"))
                updatebutton.setText("")
                updatebutton.setToolTip(translate("civilTools","An update to the civilTools workbench is available. Click here to open the addons manager."))
                updatebutton.setFlat(True)
                QtCore.QObject.connect(updatebutton,QtCore.SIGNAL("pressed()"),addonMgr)
                updatebutton.hide()
                statuswidget.addWidget(updatebutton)
                QtCore.QTimer.singleShot(2500, checkUpdates) # delay a bit the check for BIM WB update...
        else:
            if statuswidget:
                statuswidget.hide()
            else:
                # when switching workbenches, the toolbar sometimes "jumps"
                # out of the status bar to any other dock area...
                statuswidget = mw.findChild(QtGui.QToolBar,"CivilToolsStatusWidget")
                if statuswidget:
                    statuswidget.hide()

