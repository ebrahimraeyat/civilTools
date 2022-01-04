
from pathlib import Path

from PySide2 import QtCore
from PySide2.QtWidgets import QMessageBox

import FreeCADGui as Gui

from export import config


class CivilCreatePeriodFile:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_period",
            "create period file")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civil_perion",
            "Create Period File")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "time.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        import etabs_obj
        etabs = etabs_obj.EtabsModel(backup=False)
        if not etabs.success:
            QMessageBox.warning(None, 'ETABS', 'Please open etabs file!')
            return False
        etabs_filename = etabs.get_filename()
        json_file = etabs_filename.with_suffix('.json')
        if not json_file.exists():
            QMessageBox.warning(None, 'Settings', 'Please Set Options First!')
            Gui.runCommand("civiltools_settings")
            return
        tx, ty, _ = etabs.get_drift_periods()
        config.save_analytical_periods(json_file, tx, ty)
        t_file = etabs.get_filepath() / 'T.EDB'
        QMessageBox.information(None, 'Successful', f'Created Period File: {t_file}')
            

        
    def IsActive(self):
        return True


        