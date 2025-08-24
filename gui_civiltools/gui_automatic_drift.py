
from pathlib import Path

from PySide import QtCore
from PySide.QtGui import QMessageBox

import FreeCADGui as Gui


class CivilAutomaticDrift:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_automatic_drift",
            "Auto Drift")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civil_automatic_drift",
            "Get Automatically Create T.EDB file and Calculate C and K factor. Then apply. Then apply C, K, C_drift and K_drift to Etabs Model")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "automatic_drift.svg"
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
            'show_drifts.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/7f10571fab2a08b7a17ab782778e53e1/raw',
            'cfactor'
            )
        if not allow:
            return
        import find_etabs
        etabs, filename = find_etabs.find_etabs(run=False, backup=False)
        if (
            etabs is None or
            filename is None
            ):
            return
        if not etabs.diaphragm.is_diaphragm_assigned():
            QMessageBox.warning(None, 'Diaphragm Assignment', "Please Assign Diaphragm to model.")
            return
        from exporter import civiltools_config
        d = civiltools_config.get_settings_from_etabs(etabs)
        if len(d) == 0:
            QMessageBox.warning(None, 'Settings', 'Please Set Options First!')
            Gui.runCommand("civiltools_settings")
            d = civiltools_config.get_settings_from_etabs(etabs)
            if len(d) == 0:
                return
        from py_widget import drift
        win = drift.Form(etabs, d)
        find_etabs.show_win(win, in_mdi=False)
        show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True


        