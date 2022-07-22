
from pathlib import Path

from PySide2 import QtCore

import FreeCAD
import FreeCADGui as Gui



class CivilToolsDefineAxis:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_grid_lines",
            "Assign Frame Sections")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civil_assign_frame_sections",
            "Assign Frame Sections to beams and columns")
        path = str(
                   Path(__file__).parent.parent.parent / "images" / "grid_lines.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        # import find_etabs
        # etabs, filename = find_etabs.find_etabs(run=False, backup=False)
        # if (
        #     etabs is None or
        #     filename is None
        #     ):
        #     return
        from py_widget.define import define_axes
        win = define_axes.Form(etabs=None)
        Gui.Control.showDialog(win)
        
    def IsActive(self):
        return True


Gui.addCommand("civilTools_define_axis", CivilToolsDefineAxis())


        