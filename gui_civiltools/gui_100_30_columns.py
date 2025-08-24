
from pathlib import Path

from PySide import QtCore
from PySide.QtGui import QMessageBox

import FreeCADGui as Gui



class CivilTools100_30Columns:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Investigate 100-30")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Check if needed apply 100-30")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "100_30.svg"
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
            '100-30.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/bbfab4efcc50cbcfeba7288339b68c90/raw',
            'cfactor',
            n=2,
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
        if len(d) == 0:
            return
        if any([
            d.get('torsional_irregularity_groupbox', False),
            d.get('reentrance_corner_checkbox', False),
            d.get('diaphragm_discontinuity_checkbox', False),
            d.get('out_of_plane_offset_checkbox', False),
            d.get('nonparallel_system_checkbox', False),
        ]) and QMessageBox.question(None,
            "100 - 30",
            "Model has Horizontal Irregularity, Do you want to continue?",
            ) == QMessageBox.No:
            return
        from py_widget.control import columns_100_30
        win = columns_100_30.Form(etabs, d)
        find_etabs.show_win(win, in_mdi=False)
        show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True


        