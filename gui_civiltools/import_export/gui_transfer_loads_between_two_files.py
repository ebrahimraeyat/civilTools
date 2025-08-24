
from pathlib import Path

from PySide import QtCore
from PySide.QtGui import QMessageBox

import FreeCADGui as Gui



class CivilToolsTransferLoadsBetweenTwoFiles:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Transfer loads between two files")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Transfer loads between two files")
        path = str(
                   Path(__file__).parent.parent.parent / "images" / "transfer_loads_between_two_files.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        
        # from gui_civiltools.gui_check_legal import (
        #         allowed_to_continue,
        #         show_warning_about_number_of_use,
        #         )
        # allow, check = allowed_to_continue(
        #     '100-30.bin',
        #     'https://gist.githubusercontent.com/ebrahimraeyat/bbfab4efcc50cbcfeba7288339b68c90/raw',
        #     'cfactor',
        #     n=2,
        #     )
        # if not allow:
        #     return
        from py_widget.import_export import transfer_loads_between_two_files
        win = transfer_loads_between_two_files.Form()
        win.form.exec_()
        
    def IsActive(self):
        return True
    

Gui.addCommand("civiltools_transfer_loads_between_two_files", CivilToolsTransferLoadsBetweenTwoFiles())


        