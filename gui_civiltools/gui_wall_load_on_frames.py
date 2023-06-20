
from pathlib import Path

from PySide2 import QtCore
from PySide2.QtWidgets import QMessageBox

import FreeCADGui as Gui



class CivilWallLoadOnFrames:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Wall Load")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Wall Load on Frames")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "wall.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        import find_etabs
        etabs, filename = find_etabs.find_etabs(run=False, backup=False)
        if (
            etabs is None or
            filename is None
            ):
            return
        from py_widget.assign import wall_load_on_frames
        win = wall_load_on_frames.Form(etabs)
        Gui.Control.showDialog(win)
        
    def IsActive(self):
        return True


class CivilToolsUpdateLevels:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Update Levels")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Update Levels in FreeCAD with ETABS Model.")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "update_levels.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        import find_etabs
        etabs, filename = find_etabs.find_etabs(run=False, backup=False)
        if (
            etabs is None or
            filename is None
            ):
            return
        from freecad_py.assign import wall_loads
        wall_loads.update_levels(etabs)
        QMessageBox.information(None, 'Update Levels', "Levels Updated with ETABS Model.")
        
    def IsActive(self):
        return True

class CivilToolsWallLoadsGroupCommand:

    def GetCommands(self):
        return (
            "civil_wall_load_on_frames",
            "civilTools_update_levels",
        )  # a tuple of command names that you want to group


    def GetDefaultCommand(self):
        return 0

    def GetResources(self):
        return {
            "MenuText": "Wall Loads",
            "ToolTip": "Create and Apply wall loads automatically",
            "DropDownMenu": True,
            "Exclusive": True,
        }

Gui.addCommand('civil_wall_load_on_frames', CivilWallLoadOnFrames())
Gui.addCommand("civilTools_update_levels", CivilToolsUpdateLevels())
Gui.addCommand('civiltools_wall_load', CivilToolsWallLoadsGroupCommand())
        