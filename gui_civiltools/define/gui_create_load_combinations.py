
from pathlib import Path

from PySide2 import QtCore
from PySide2.QtWidgets import QMessageBox

import FreeCADGui as Gui



class CivilToolsCreateLoadCombinations:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Create Load Combinations")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Create Load Combinations")
        path = str(
                   Path(__file__).parent.absolute().parent.parent / "images" / "load_combinations.svg"
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
        from py_widget.define import create_load_combinations
        win = create_load_combinations.Form(etabs)
        find_etabs.show_win(win, in_mdi=False)
        # Gui.Control.showDialog(win)
        # show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True


class CivilToolsCreatePushLoadCombination:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Create Push Combo")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Create Push Load Combinations")
        path = str(
                   Path(__file__).parent.absolute().parent.parent / "images" / "load_combination.svg"
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
        from py_widget.define import create_load_combination
        win = create_load_combination.Form(etabs)
        find_etabs.show_win(win, in_mdi=False)
        # show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True


class CivilToolsAddLoadCombinationsToF2k:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Add to F2K")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Add Load Combinations to F2K file")
        path = str(
                   Path(__file__).parent.absolute().parent.parent / "images" / "load_combinations_to_f2k.svg"
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
        from py_widget.define import load_combinations_to_f2k
        win = load_combinations_to_f2k.Form(etabs)
        find_etabs.show_win(win, in_mdi=False)
        # show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True


class CivilToolsLoadCombinationGroupCommand:

    def GetCommands(self):
        return (
            "civilTools_create_load_combinations",
            "civilTools_create_push_load_combinations",
            "civiltools_load_combinations_to_f2k",
        )  # a tuple of command names that you want to group

    # def Activated(self, index):
    #     commands = self.GetCommands()
    #     command_name = commands[index]
    #     Gui.runCommand(command_name)

    def GetDefaultCommand(self):
        return 0

    def GetResources(self):
        return {
            "MenuText": "Load Combination",
            "ToolTip": "Create Load combinations",
            "DropDownMenu": True,
            "Exclusive": True,
        }

        
Gui.addCommand("civilTools_create_load_combinations", CivilToolsCreateLoadCombinations())
Gui.addCommand("civilTools_create_push_load_combinations", CivilToolsCreatePushLoadCombination())
Gui.addCommand('civiltools_load_combinations_to_f2k', CivilToolsAddLoadCombinationsToF2k())
Gui.addCommand('civiltools_load_combinations', CivilToolsLoadCombinationGroupCommand())