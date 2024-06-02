
from pathlib import Path

from PySide2 import QtCore

import FreeCADGui as Gui


class CiviltoosExportPlansToDxf:
    """Gui command for import DXF files."""

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "CIVILTOOLS",
            "Export plans to dxf")
        tool_tip = QtCore.QT_TRANSLATE_NOOP(
            "CIVILTOOLS",
            "Export plan of beams and columns to dxf")
        path = str(
                   Path(__file__).parent.absolute().parent.parent / "images" / "dxf.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tool_tip}

    def Activated(self):
        import find_etabs
        etabs, filename = find_etabs.find_etabs(run=False, backup=False)
        if (
            etabs is None or
            filename is None
            ):
            return
        from py_widget.import_export import export_plans_to_dxf
        win = export_plans_to_dxf.Form(etabs)
        find_etabs.show_win(win, in_mdi=False)

    def IsActive(self):
        return True


Gui.addCommand('civiltoos_export_plans_to_dxf', CiviltoosExportPlansToDxf())