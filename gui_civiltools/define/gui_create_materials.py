

from pathlib import Path

from PySide import QtCore
from PySide.QtGui import QMessageBox

import FreeCADGui as Gui


class CivilToolsCreateMaterials:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools_create_materials",
            "Create Materials")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools_create_materials",
            "Create materials")
        path = str(
                   Path(__file__).parent.parent.absolute().parent / "images" / "materials.svg"
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
        from py_widget.define import create_materials
        win = create_materials.Form(etabs)
        find_etabs.show_win(win, in_mdi=False)

Gui.addCommand("civilTools_create_materials", CivilToolsCreateMaterials())