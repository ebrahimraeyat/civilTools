
from pathlib import Path

from PySide import QtCore
from PySide.QtGui import QMessageBox

import FreeCADGui as Gui


class CivilToolsMatchPropery:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools_match_property",
            "Match Property")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools_match_property",
            "Assign Ev Automatically to ETABS Model")
        path = str(
                   Path(__file__).parent.absolute().parent.parent / "images" / "match_property.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        
        from gui_civiltools.gui_check_legal import (
                allowed_to_continue,
                show_warning_about_number_of_use,
                )
        allow, check = allowed_to_continue(
            'match_property.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/0b48ce4e8e29e833f0b9eb591d996649/raw',
            'cfactor'
            )
        if not allow:
            return
        import find_etabs
        etabs, filename = find_etabs.find_etabs(run=False, backup=True)
        if (
            etabs is None or
            filename is None
            ):
            return

        try:
            ret = etabs.SapModel.SelectObj.GetSelected()
        except IndexError:
            QMessageBox.warning(None, "Select Object", "Select atleast one Frame or Area Object.")
            return
        if ret[0] > 1:
            QMessageBox.warning(None, "Select Object", "Select only one Frame or Area Object.")
            return

        etabs.SapModel.SelectObj.ClearSelection()
        obj_ = ret[2][0]
        etabs.unlock_model()
            
        from py_widget.tools import match_property
        win = match_property.Form(etabs, obj_)
        Gui.Control.showDialog(win)
        show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True

Gui.addCommand("civilTools_match_property", CivilToolsMatchPropery())
        