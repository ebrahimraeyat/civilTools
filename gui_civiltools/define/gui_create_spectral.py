

from pathlib import Path

from PySide2 import QtCore

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
        etabs, _ = find_etabs.find_etabs(run=False, backup=False, show_warning=False)
        # if (
        #     etabs is None or
        #     filename is None
        #     ):
        #     return
        from py_widget.define import create_spectral
        win = create_spectral.Form(etabs)
        find_etabs.show_win(win, in_mdi=False)