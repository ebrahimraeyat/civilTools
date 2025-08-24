
from pathlib import Path

from PySide import QtCore
from PySide.QtGui import QMessageBox

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
        from exporter import civiltools_config
        d = civiltools_config.get_settings_from_etabs(etabs)
        from py_widget.control import control_joint_shear
        win = control_joint_shear.Form(etabs, d)
        find_etabs.show_win(win, in_mdi=False)
        
    def IsActive(self):
        return True


Gui.addCommand("civilTools_control_joint_shear", CivilToolsJointShear())