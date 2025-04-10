
from pathlib import Path

from PySide2 import QtCore
from PySide2.QtWidgets import QMessageBox

import FreeCADGui as Gui


class CivilToolsDiaphragmAppliedForces:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools_diaphragm_forces",
            "Diaphragm Forces")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools_diaphragm_forces",
            "Create The Diaphragm Earthquake Forces Files For Every Story That User Select.")
        path = str(
                   Path(__file__).parent.absolute().parent.parent / "images" / "assign_ev.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        
        # from gui_civiltools.gui_check_legal import (
        #         allowed_to_continue,
        #         show_warning_about_number_of_use,
        #         )
        # allow, check = allowed_to_continue(
        #     'assign_ev.bin',
        #     'https://gist.githubusercontent.com/ebrahimraeyat/20078f898b9c4a99bd5c8dd14ef7d012/raw',
        #     'cfactor'
        #     )
        # if not allow:
        #     return
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
        
        from py_widget.control import diaphragm_applied_forces
        win = diaphragm_applied_forces.Form(etabs, d)
        find_etabs.show_win(win, in_mdi=False)
        # show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True

Gui.addCommand("civilTools_diaphragm_applied_forces", CivilToolsDiaphragmAppliedForces())
        