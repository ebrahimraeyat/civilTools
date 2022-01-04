
from pathlib import Path

from PySide2 import QtCore
from PySide2.QtWidgets import QMessageBox

import FreeCADGui as Gui



class CivilEarthquakeFactor:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "Civil",
            "Earthquake Factors")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "Civil",
            "Calculate Earthquake Factors and Write to ETABS Model")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "earthquake.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        from gui_civiltools.gui_check_legal import (
                allowed_to_continue,
                show_warning_about_number_of_use,
                )
        allow, check = allowed_to_continue(
            'export_to_etabs.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/7f10571fab2a08b7a17ab782778e53e1/raw',
            'cfactor'
            )
        if not allow:
            return
        import etabs_obj
        etabs = etabs_obj.EtabsModel()
        if not etabs.success:
            QMessageBox.warning(None, 'ETABS', 'Please open etabs file!')
            return False
        etabs_filename = etabs.get_filename()
        json_file = etabs_filename.with_suffix('.json')
        if not json_file.exists():
            QMessageBox.warning(None, 'Settings', 'Please Set Options First!')
            Gui.runCommand("civiltools_settings")
            return
        from py_widget import earthquake_factor
        win = earthquake_factor.Form(etabs, json_file)
        Gui.Control.showDialog(win)
        show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True
        