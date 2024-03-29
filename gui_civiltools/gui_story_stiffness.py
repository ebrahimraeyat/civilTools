
from pathlib import Path

from PySide2 import QtCore

import FreeCADGui as Gui


class CivilStoryStiffness:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_stiffness",
            "Story Stiffness")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civil_stiffness",
            "Get Story Stiffness")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "stiffness.svg"
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
            'stiffness.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/e5635c17392c73540a46761a7247836e/raw',
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
        from py_widget import get_siffness_story_way
        win = get_siffness_story_way.Form(etabs)
        find_etabs.show_win(win, in_mdi=False)
        show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True


        