

from pathlib import Path

from PySide import QtCore
from PySide.QtGui import QMessageBox

import FreeCADGui as Gui


class CivilToolsCreateSpectral:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools_create_spectral",
            "Create Spectral")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools_create_spectral",
            "Create Spectral for Structure that specified user.")
        path = str(
                   Path(__file__).parent.parent.absolute().parent / "images" / "spectral.svg"
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
        if len(d) == 0:
            QMessageBox.warning(None, 'Settings', 'Please Set Options First!')
            Gui.runCommand("civiltools_settings")
            d = civiltools_config.get_settings_from_etabs(etabs)
            if len(d) == 0:
                return
        from py_widget.define import create_spectral
        win = create_spectral.Form(etabs, d)
        find_etabs.show_win(win, in_mdi=False)