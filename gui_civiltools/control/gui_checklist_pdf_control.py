
from pathlib import Path

from PySide2 import QtCore

import FreeCADGui as Gui



class CivilToolsChecklistPDFControl:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Check List")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Show The Check List in PDF Format")
        path = str(
                   Path(__file__).parent.absolute().parent.parent / "images" / "checklist_pdf_control.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        civiltools_path = Path(__file__).parent.parent.parent
        import webbrowser
        path = civiltools_path / "db" / "checklist.pdf"
        webbrowser.open_new(str(path))
        
    def IsActive(self):
        return True


Gui.addCommand("civilTools_checklist_pdf_control", CivilToolsChecklistPDFControl())