
from pathlib import Path

from PySide2 import QtCore

import FreeCADGui as Gui



class CivilToolsAssignFrameSections:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_assign_frame_sections",
            "Assign Frame Sections")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civil_assign_frame_sections",
            "Assign Frame Sections to beams and columns")
        path = str(
                   Path(__file__).parent.parent.parent / "images" / "assign_frame_sections.svg"
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
        import find_etabs
        etabs, filename = find_etabs.find_etabs(run=False, backup=False)
        if (
            etabs is None or
            filename is None
            ):
            return
        from py_widget.assign import assign_frame_sections
        win = assign_frame_sections.Form(etabs)
        Gui.Control.showDialog(win)
        show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True


class CivilToolsCreateFrameSections:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools_create_frame_sections",
            "Create Frame Sections")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools_create_frame_sections",
            "Create Frame Sections For Beams and Columns")
        path = str(
                   Path(__file__).parent.parent.parent / "images" / "create_frame_sections.svg"
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
        import find_etabs
        etabs, filename = find_etabs.find_etabs(run=False, backup=False)
        if (
            etabs is None or
            filename is None
            ):
            return
        
        from py_widget.define import define_frame_sections
        win = define_frame_sections.Form(etabs)
        find_etabs.show_win(win)
        show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True


class CivilToolsFrameSectionsGroupCommand:

    def GetCommands(self):
        return (
            "civilTools_create_frame_sections",
            "civilTools_assign_frame_sections",
        )  # a tuple of command names that you want to group

    # def Activated(self, index):
    #     commands = self.GetCommands()
    #     command_name = commands[index]
    #     Gui.runCommand(command_name)

    def GetDefaultCommand(self):
        return 0

    def GetResources(self):
        return {
            "MenuText": "Frame Section",
            "ToolTip": "Create and Assign Frame Sections",
            "DropDownMenu": True,
            "Exclusive": True,
        }

        
Gui.addCommand("civilTools_create_frame_sections", CivilToolsCreateFrameSections())
Gui.addCommand("civilTools_assign_frame_sections", CivilToolsAssignFrameSections())
Gui.addCommand("civiltools_frame_sections", CivilToolsFrameSectionsGroupCommand())


        