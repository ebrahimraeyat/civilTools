
from pathlib import Path

from PySide2 import QtCore
from PySide2.QtWidgets import QMessageBox

import FreeCADGui as Gui



class CivilToolsUpdateWallLoadOnFrames:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Update Wall Loads")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Update Wall Load on Frames")
        path = str(
                   Path(__file__).parent.parent.parent / "images" / "wall.svg"
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
        beams, _ = etabs.frame_obj.get_beams_columns(types=range(10))
        etabs.frame_obj.update_gravity_loads_from_wall(beams)
        QMessageBox.information(None, 'Succesfull', "All Loads updated!")
        return None
        
    def IsActive(self):
        return True


# class CivilToolsUpdateModelGroupCommand:

#     def GetCommands(self):
#         return (
#             "civil_wall_load_on_frames",
#             "civilTools_update_levels",
#         )  # a tuple of command names that you want to group


#     def GetDefaultCommand(self):
#         return 0

#     def GetResources(self):
#         return {
#             "MenuText": "Wall Loads",
#             "ToolTip": "Create and Apply wall loads automatically",
#             "DropDownMenu": True,
#             "Exclusive": True,
#         }

Gui.addCommand('civiltools_update_wall_load_on_frames', CivilToolsUpdateWallLoadOnFrames())
# Gui.addCommand('civiltools_update_model', CivilToolsUpdateModelGroupCommand())
        