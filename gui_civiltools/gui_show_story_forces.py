
from pathlib import Path

from PySide import QtCore

import FreeCADGui as Gui


class CivilStoryForces:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_show_story_forces",
            "Story Forces")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civil_show_story_forces",
            "Show Stories Forces")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "shear.svg"
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
        from py_widget.control import shear_story
        win = shear_story.Form(etabs)
        Gui.Control.showDialog(win)
        
    def IsActive(self):
        return True


        