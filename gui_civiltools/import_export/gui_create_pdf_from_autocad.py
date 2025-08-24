
from pathlib import Path

from PySide import QtCore

import FreeCADGui as Gui


class CiviltoosCreatePdfFromAutocad:
    """Gui command for create pdf from autocad."""

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "CIVILTOOLS",
            "Dwg to pdf")
        tool_tip = QtCore.QT_TRANSLATE_NOOP(
            "CIVILTOOLS",
            "Create Pdf From Autocad")
        path = str(
                   Path(__file__).parent.absolute().parent.parent / "images" / "dwg_to_pdf.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tool_tip}

    def Activated(self):
        import find_etabs
        from py_widget.import_export import export_dwg_to_pdf
        win = export_dwg_to_pdf.Form()
        find_etabs.show_win(win, in_mdi=False)

    def IsActive(self):
        return True


Gui.addCommand('civiltoos_dwg_to_pdf', CiviltoosCreatePdfFromAutocad())