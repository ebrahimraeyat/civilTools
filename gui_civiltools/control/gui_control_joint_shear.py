
from pathlib import Path

from PySide2 import QtCore

import FreeCADGui as Gui



class CivilToolsJointShear:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Joint Shear")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Create joint shear file and show the results")
        path = str(
                   Path(__file__).parent.absolute().parent.parent / "images" / "joint_shear.svg"
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
        from py_widget.control import control_joint_shear
        win = control_joint_shear.Form(etabs)
        Gui.Control.showDialog(win)
        # show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True


Gui.addCommand("civilTools_control_joint_shear", CivilToolsJointShear())