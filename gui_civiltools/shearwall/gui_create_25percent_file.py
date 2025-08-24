
from pathlib import Path

from PySide import QtCore
from PySide.QtGui import QMessageBox

import FreeCADGui as Gui



class CivilToolsCreate_25Percent_File:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Create 25Percent")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Creates The 25 Percent Model File")
        path = str(
                   Path(__file__).parent.absolute().parent.parent / "images" / "create_25percent_file.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        import find_etabs
        etabs, filename = find_etabs.find_etabs(run=False, backup=True)
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
        if len(d) == 0:
            return
        from py_widget.shearwall import create_25percent_file
        win = create_25percent_file.Form(etabs, d)
        find_etabs.show_win(win, in_mdi=False)
        # show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True


Gui.addCommand("civilTools_create_25percent_file", CivilToolsCreate_25Percent_File())