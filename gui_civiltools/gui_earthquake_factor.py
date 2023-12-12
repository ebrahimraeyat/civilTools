
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
        import find_etabs
        etabs, filename = find_etabs.find_etabs(run=False, backup=False)
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
        d = civiltools_config.get_settings_from_etabs(etabs)
        if len(d) == 0:
            return
        second_system = d.get('activate_second_system', False)
        if second_system:
            if QMessageBox.question(None, 'Not Implemented',
                                 "You have two systems in height, civiltools can't apply earthquake to this type of system\nYou can apply it via Drift command, Do you want to apply it?") == QMessageBox.Yes:
                from py_widget import drift
                win = drift.Form(etabs)
                win.form.create_t_file_box.setChecked(True)
                win.form.structuretype_groupbox.setEnabled(True)
                find_etabs.show_win(win, in_mdi=False)
                return
        from py_widget import earthquake_factor
        win = earthquake_factor.Form(etabs)
        find_etabs.show_win(win, in_mdi=False)
        show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True
        