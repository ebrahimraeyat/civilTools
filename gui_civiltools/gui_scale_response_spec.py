
from pathlib import Path

from PySide2 import QtCore, QtWidgets

import FreeCADGui as Gui


class CivilScaleResponseSpec:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_scale_response_spec",
            "Response Spec.")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civil_scale_response_spec",
            "Scale Response Spectrum Analysis")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "balance.svg"
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
            'response_spectrum.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/2370d564be6b4ba2508f8314a3358970/raw',
            'cfactor',
            n=2,
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
        from py_widget import response_spectrum
        win = response_spectrum.Form(etabs, d)
        find_etabs.show_win(win, in_mdi=False)
        show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True

        