

from pathlib import Path

from PySide2 import QtCore

import FreeCADGui as Gui


class CivilToolsSettings:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_settings",
            "Settings")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civil_settings",
            "Settings")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "automatic.svg"
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
        from py_widget import settings
        win = settings.Form(etabs)
        find_etabs.show_win(win, in_mdi=False)