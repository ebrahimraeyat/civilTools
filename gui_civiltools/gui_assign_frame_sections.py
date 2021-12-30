
from pathlib import Path

from PySide2 import QtCore

import FreeCADGui as Gui



class CivilAssignFrameSections:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_assign_frame_sections",
            "Assign Frame Sections")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civil_assign_frame_sections",
            "Assign Frame Sections to beams and columns")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "assign_frame_sections.svg"
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
            'assign_frame_section.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/7a72a787854de95017f389e2936f75d5/raw',
            'cfactor',
            n=5,
            )
        if not allow:
            return
        import etabs_obj
        etabs = etabs_obj.EtabsModel(backup=False)
        if not etabs.success:
            from PySide2.QtWidgets import QMessageBox
            QMessageBox.warning(None, 'ETABS', 'Please open etabs file!')
            return False
        from py_widget.assign import assign_frame_sections
        win = assign_frame_sections.Form(etabs)
        Gui.Control.showDialog(win)
        show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True


        