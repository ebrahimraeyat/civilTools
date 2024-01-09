
from pathlib import Path

from PySide2 import QtCore, QtWidgets

import FreeCADGui as Gui


class CivilShowAj:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_show_aj",
            "Show Aj")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civil_show_aj",
            "Show Static and Dynamic Aj Tables and Apply Aj to ETABS Model")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "show_aj.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        from gui_civiltools.gui_check_legal import (
            allowed_to_continue,
            show_warning_about_number_of_use
        )
        allow, check = allowed_to_continue(
            'export_to_etabs.bin',
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
        from exporter import civiltools_config
        d = civiltools_config.get_settings_from_etabs(etabs)
        if len(d) == 0:
            QtWidgets.QMessageBox.warning(None, 'Settings', 'Please Set Options First!')
            Gui.runCommand("civiltools_settings")
            d = civiltools_config.get_settings_from_etabs(etabs)
            if len(d) == 0:
                return
        from py_widget import aj_correction
        win = aj_correction.Form(etabs, d)
        find_etabs.show_win(win, in_mdi=False)
        show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True



        