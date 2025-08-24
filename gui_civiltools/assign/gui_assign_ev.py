
from pathlib import Path

from PySide import QtCore
from PySide.QtGui import QMessageBox

import FreeCADGui as Gui


class CivilToolsAssignEv:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools_assign_ev",
            "Assign Ev")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civil_assign_ev",
            "Assign Ev Automatically to ETABS Model")
        path = str(
                   Path(__file__).parent.absolute().parent.parent / "images" / "assign_ev.svg"
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
            'assign_ev.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/20078f898b9c4a99bd5c8dd14ef7d012/raw',
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
        from exporter import civiltools_config
        d = civiltools_config.load(etabs)
        if len(d) == 0:
            QMessageBox.warning(None, 'Settings', 'Please Set Options First!')
            Gui.runCommand("civiltools_settings")
            d = civiltools_config.load(etabs)
            if len(d) == 0:
                return
        risk_level = d.get('risk_level', None)
        if risk_level  is not None and \
            risk_level == 'خیلی زیاد' and \
            QMessageBox.question(
                None,
                'risk level',
                'Your are in "High Risk Level Zone", It is not recommended that apply EV individually, Do you want to continue?',
                ) == QMessageBox.No:
            return
        
        from py_widget.assign import assign_ev
        win = assign_ev.Form(etabs, d)
        find_etabs.show_win(win, in_mdi=False)
        show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True

Gui.addCommand("civilTools_assign_ev", CivilToolsAssignEv())
        