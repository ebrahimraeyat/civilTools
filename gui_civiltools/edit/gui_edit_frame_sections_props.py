
from pathlib import Path

from PySide import QtCore
from PySide.QtGui import QMessageBox

import FreeCADGui as Gui


class CivilToolsEditFrameSectionsProps:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools_edit_frame_sections_props",
            "Edit Frame Sections Props")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civil_edit_frame_sections_props",
            "Edit Frame Sections properties like fc, fy, etc.")
        path = str(
                   Path(__file__).parent.absolute().parent.parent / "images" / "property_editor.svg"
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
            'edit_frame_props.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/ea2d41b5035c0fb1182b290411766364/raw',
            'cfactor'
            )
        if not allow:
            return
        import find_etabs
        etabs, filename = find_etabs.find_etabs(run=False, backup=True)
        if (
            etabs is None or
            filename is None
            ):
            return
        
        from py_widget.edit import edit_frame_sections_props
        win = edit_frame_sections_props.Form(etabs)
        find_etabs.show_win(win, in_mdi=False)
        show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True

Gui.addCommand("civiltools_edit_frame_sections_props", CivilToolsEditFrameSectionsProps())
        