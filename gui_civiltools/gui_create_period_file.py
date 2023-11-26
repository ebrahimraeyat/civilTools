
from pathlib import Path

from PySide2 import QtCore
from PySide2.QtWidgets import QMessageBox

import FreeCADGui as Gui

from exporter import civiltools_config


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
        import find_etabs
        etabs, filename = find_etabs.find_etabs(run=False, backup=False)
        if (
            etabs is None or
            filename is None
            ):
            return
        d = civiltools_config.get_settings_from_etabs(etabs)
        if len(d) == 0:
            QMessageBox.warning(None, 'Settings', 'Please Set Options First!')
            Gui.runCommand("civiltools_settings")
        tx, ty, _ = etabs.get_drift_periods()
        civiltools_config.save_analytical_periods(etabs, tx, ty)
        t_file = filename.with_name(etabs.get_file_name_without_suffix() + "_T.EDB")
        QMessageBox.information(None, 'Successful', f'Created Period File: {t_file}')
        
    def IsActive(self):
        return True


        