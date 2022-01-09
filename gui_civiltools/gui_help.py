
from pathlib import Path

from PySide2 import QtCore


class CivilToolsHelp:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "CivilTools")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "CivilTools Help")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "help.png"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        civiltools_path = Path(__file__).absolute().parent.parent
        import webbrowser
        path = civiltools_path / "help" / "help.pdf"
        webbrowser.open_new(str(path))
        
    def IsActive(self):
        return True


        