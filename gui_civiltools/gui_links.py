
from pathlib import Path

from PySide import QtCore
from PySide.QtGui import QMessageBox

import FreeCADGui as Gui



class CivilToolsAparatSite:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Aparat Site")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Open Aparat Site")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "general" / "Logo_Aparat.jpg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        
        import webbrowser
        webbrowser.open('https://www.aparat.com/ebrahimraeyat/videos')
        
    def IsActive(self):
        return True


Gui.addCommand('civiltoos_aparat_site', CivilToolsAparatSite())
        