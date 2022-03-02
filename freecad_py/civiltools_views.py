#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2018 Yorik van Havre <yorik@uncreated.net>              *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Library General Public License for more details.                  *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with this program; if not, write to the Free Software   *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************

"""This module contains FreeCAD commands for the civilTools workbench"""


import sys
from pathlib import Path

from PySide2.QtCore import Qt
import FreeCAD, Draft

from CivilToolsTranslateUtils import *

import civiltools_rc

UPDATEINTERVAL = 2000 # number of milliseconds between civiltools Views window update



class CivilToolsViews:


    def GetResources(self):

        return {'Pixmap'  : str(Path(__file__).parent.parent / "images" / "civiltools_views.svg"),
                'MenuText': QT_TRANSLATE_NOOP("CivilTools_Views", "Views manager"),
                'ToolTip' : QT_TRANSLATE_NOOP("CivilTools_Views", "Shows or hides the views manager"),
                'Accel': 'Ctrl+9'}

    def Activated(self):

        import FreeCADGui
        from PySide import QtCore,QtGui
        mw = FreeCADGui.getMainWindow()
        vm = findWidget(mw)
        civiltoolsviewsbutton = None
        st = mw.statusBar()
        statuswidget = st.findChild(QtGui.QToolBar,"CivilToolsStatusWidget")
        if statuswidget:
            if hasattr(statuswidget,"civiltoolsviewsbutton"):
                civiltoolsviewsbutton = statuswidget.civiltoolsviewsbutton
        if vm:
            if vm.isVisible():
                vm.hide()
                if civiltoolsviewsbutton:
                    civiltoolsviewsbutton.setChecked(False)
                    FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/civilTools").SetBool("RestoreCivilToolsViews",False)
            else:
                vm.show()
                if civiltoolsviewsbutton:
                    civiltoolsviewsbutton.setChecked(True)
                    FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/civilTools").SetBool("RestoreCivilToolsViews",True)
                self.update()
        else:
            vm = QtGui.QDockWidget()

            # create the dialog
            dialog = FreeCADGui.PySideUic.loadUi(str(Path(__file__).parent.parent / 'widgets'   / 'view' / 'dialogViews.ui'))
            vm.setWidget(dialog)
            vm.tree = dialog.tree
            vm.beam = dialog.beam
            vm.column = dialog.column
            vm.brace = dialog.brace
            vm.shear_wall = dialog.shear_wall
            vm.arch_wall = dialog.arch_wall
            vm.floor = dialog.floor
            vm.wireframe = dialog.wireframe

            # set button sizes
            size = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/General").GetInt("ToolbarIconSize",24)
            for button in [
                           dialog.button_refresh,
                           dialog.buttonToggle,
                           dialog.buttonIsolate,
                        ]:
                button.setMaximumSize(QtCore.QSize(size+4,size+4))
                button.setIconSize(QtCore.QSize(size,size))

            # set button icons
            import Arch_rc,Draft_rc
            dialog.buttonIsolate.setIcon(QtGui.QIcon(":/icons/view-refresh.svg"))
            dialog.beam.stateChanged.connect(self.view_objects)
            dialog.column.stateChanged.connect(self.view_objects)
            dialog.brace.stateChanged.connect(self.view_objects)
            dialog.shear_wall.stateChanged.connect(self.view_objects)
            dialog.arch_wall.stateChanged.connect(self.view_objects)
            dialog.floor.stateChanged.connect(self.view_objects)
            dialog.wireframe.stateChanged.connect(self.view_objects)
            dialog.button_refresh.clicked.connect(self.update)

            # connect signals
            dialog.buttonToggle.clicked.connect(self.toggle)
            dialog.buttonIsolate.clicked.connect(self.isolate)
            # dialog.buttonSaveView.clicked.connect(self.saveView)
            dialog.tree.itemClicked.connect(self.select)
            dialog.tree.itemClicked.connect(self.view_objects)
            dialog.tree.itemDoubleClicked.connect(self.toggle)

            # set the dock widget
            vm.setObjectName("CivilTools Views Manager")
            vm.setWindowTitle(translate("civilTools","CivilTools View"))
            mw = FreeCADGui.getMainWindow()
            mw.addDockWidget(QtCore.Qt.LeftDockWidgetArea, vm)

            # restore saved settings
            pref = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/civilTools")
            vm.tree.setColumnWidth(0,pref.GetInt("ViewManagerColumnWidth",100))
            vm.setFloating(pref.GetFloat("ViewManagerFloating",False))

            # check the status bar button
            if civiltoolsviewsbutton:
                civiltoolsviewsbutton.setChecked(True)
            pref.SetBool("RestoreCivilToolsViews",True)

            self.update()

    def update(self,retrigger=True):

        "updates the view manager"

        from PySide import QtCore,QtGui
        import FreeCADGui
        vm = findWidget()
        if vm and FreeCAD.ActiveDocument and vm.isVisible():
            vm.tree.clear()
            for obj in FreeCAD.ActiveDocument.Objects:
                if hasattr(obj, 'IfcType') and obj.IfcType == 'Building Storey':
                    u = FreeCAD.Units.Quantity(obj.Placement.Base.z,FreeCAD.Units.Length).UserString
                    it = QtGui.QTreeWidgetItem([obj.Label,u])
                    # it.setFlags(it.flags() | QtCore.Qt.ItemIsEditable)
                    # it.setCheckState(Qt.Checked)
                    it.setToolTip(0,obj.Name)
                    if obj.ViewObject:
                        if hasattr(obj.ViewObject,"Proxy") and hasattr(obj.ViewObject.Proxy,"getIcon"):
                            it.setIcon(0,QtGui.QIcon(obj.ViewObject.Proxy.getIcon()))
                    vm.tree.addTopLevelItem(it)
                    if obj in FreeCADGui.Selection.getSelection():
                        it.setSelected(True)
        # if retrigger:
        #     QtCore.QTimer.singleShot(UPDATEINTERVAL, self.update)

        # save state
        pref = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/civilTools")
        pref.SetInt("ViewManagerColumnWidth",vm.tree.columnWidth(0))
        pref.SetFloat("ViewManagerFloating",vm.isFloating())

    def select(self,item,column=None):

        "selects a doc object corresponding to an item"

        import FreeCADGui
        vm = findWidget()
        if vm:
            for i in range(vm.tree.topLevelItemCount()):
                item = vm.tree.topLevelItem(i)
                obj = FreeCAD.ActiveDocument.getObject(item.toolTip(0))
                if obj:
                    if item.isSelected():
                        FreeCADGui.Selection.addSelection(obj)
                    else:
                        FreeCADGui.Selection.removeSelection(obj)

    def view_objects(self):
        vm = findWidget()
        selected_stories = [item.toolTip(0) for item in vm.tree.selectedItems()]
        show_beam = vm.beam.isChecked()
        show_column = vm.column.isChecked()
        show_brace = vm.brace.isChecked()
        show_floor = vm.floor.isChecked()
        show_shear_wall = vm.shear_wall.isChecked()
        show_arch_wall = vm.arch_wall.isChecked()
        wireframe = vm.wireframe.isChecked()

        for obj in FreeCAD.ActiveDocument.Objects:
            if Draft.getType(obj) == "Sketcher::SketchObject":
                continue
            if hasattr(obj, 'Proxy') and hasattr(obj.Proxy, 'Type') and obj.Proxy.Type == 'Profile':
                continue
            inlists = obj.InList
            story = None
            if inlists:
                for o in inlists:
                    if hasattr(o, 'IfcType') and o.IfcType == 'Building Storey':
                        story = o
                        break
            show_story = False
            show_obj = True
            if story is None or story.Name in selected_stories:
                show_story = True

            if hasattr(obj, 'IfcType') and obj.IfcType == 'Beam':
                show_obj = show_beam and not wireframe
            if hasattr(obj, 'IfcType') and obj.IfcType == 'Column':
                show_obj = show_column and not wireframe
            if hasattr(obj, 'IfcType') and obj.IfcType == 'Wall':
                show_obj = show_arch_wall
            if obj.Label.startswith('W') and hasattr(obj,'MakeFace'):
                show_obj = show_shear_wall
            if obj.Label.startswith('F') and hasattr(obj,'MakeFace'):
                show_obj = show_floor
            show = show_story and show_obj
            show_object(obj, show)
        FreeCAD.ActiveDocument.recompute()
                
    def toggle(self):

        "toggle selected item on/off"

        vm = findWidget()
        if vm:
            for item in vm.tree.selectedItems():
                obj = FreeCAD.ActiveDocument.getObject(item.toolTip(0))
                if obj:
                    show = not(obj.ViewObject.Visibility)
                    show_object(obj, show)
            FreeCAD.ActiveDocument.recompute()

    def isolate(self):

        "turns all items off except the selected ones"

        vm = findWidget()
        if vm:
            onnames = [item.toolTip(0) for item in vm.tree.selectedItems()]
            for i in range(vm.tree.topLevelItemCount()):
                item = vm.tree.topLevelItem(i)
                name = item.toolTip(0)
                obj = FreeCAD.ActiveDocument.getObject(name)
                if obj and hasattr(obj, 'ViewObject'):
                    if name not in onnames:
                        obj.ViewObject.hide()
                    else:
                        obj.ViewObject.show()
            FreeCAD.ActiveDocument.recompute()

    # def saveView(self):

    #     "save the current camera angle to the selected item"

    #     vm = findWidget()
    #     if vm:
    #         for item in vm.tree.selectedItems():
    #             obj = FreeCAD.ActiveDocument.getObject(item.toolTip(0))
    #             if obj:
    #                 if hasattr(obj.ViewObject.Proxy,"writeCamera"):
    #                     obj.ViewObject.Proxy.writeCamera()
    #     FreeCAD.ActiveDocument.recompute()




# These functions need to be localized outside the command class, as they are used outside this module



def findWidget(mw=None):

    "finds the manager widget, if present"

    import FreeCADGui
    from PySide import QtGui
    if mw is None:
        mw = FreeCADGui.getMainWindow()
    vm = mw.findChild(QtGui.QDockWidget,"CivilTools Views Manager")
    if vm:
        return vm
    return None

def show_object(obj, show : bool):
    if show:
        obj.ViewObject.show()
    else:
        obj.ViewObject.hide()

def iter_items(root, column=0):
    def recurse(parent, column=0):
        for row in range(parent.rowCount()):
            child = parent.child(row, column)
            yield child
            if child.hasChildren():
                yield from recurse(child)
    if root is not None:
        yield from recurse(root, column)

def show(item,column=None):

    "item has been double-clicked"

    import FreeCADGui
    obj = None
    vm = findWidget()
    # if isinstance(item,str) or ((sys.version_info.major < 3) and isinstance(item,unicode)):
    #     # called from Python code
    #     obj = FreeCAD.ActiveDocument.getObject(item)
    # else:
    #     # called from GUI
    #     if column == 1:
    #         # user clicked the level field
    #         if vm:
    #             vm.tree.editItem(item,column)
    #             return
    #     else:
    #         # TODO find a way to not edit the object name
    obj = FreeCAD.ActiveDocument.getObject(item.toolTip(0))
    if obj:
        FreeCADGui.Selection.clearSelection()
        FreeCADGui.Selection.addSelection(obj)
        FreeCADGui.runCommand("Draft_SelectPlane")
    if vm:
        # store the last double-clicked item for the civilTools WPView command
        if isinstance(item,str) or ((sys.version_info.major < 3) and isinstance(item,unicode)):
            vm.lastSelected = item
        else:
            vm.lastSelected = item.toolTip(0)
