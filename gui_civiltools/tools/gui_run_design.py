
from pathlib import Path

from PySide2 import QtCore
from PySide2.QtWidgets import QMessageBox

import FreeCADGui as Gui



class CivilToolsRunAndConcreteFrameDesign:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Run & Design Concrete")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Run Model and Design Concrete Frames")
        path = str(
                   Path(__file__).parent.absolute().parent.parent / "images" / "run_concrete_design.svg"
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
        etabs.run_analysis()
        etabs.start_design()
        QMessageBox.information(None, 'Run & Design',
            'Runnig and Design of Concrete Frame Desing Finished.')
        
    def IsActive(self):
        return True


class CivilToolsRunAndDesignGroupCommand:

    def GetCommands(self):
        return (
            "civilTools_run_and_design_concrete_frame",
        )  # a tuple of command names that you want to group

    # def Activated(self, index):
    #     commands = self.GetCommands()
    #     command_name = commands[index]
    #     Gui.runCommand(command_name)

    def GetDefaultCommand(self):
        return 0

    def GetResources(self):
        return {
            "MenuText": "Run & Design",
            "ToolTip": "Run and Design the model.",
            "DropDownMenu": True,
            "Exclusive": True,
        }

        
Gui.addCommand("civilTools_run_and_design_concrete_frame", CivilToolsRunAndConcreteFrameDesign())
Gui.addCommand('civiltools_run_and_design', CivilToolsRunAndDesignGroupCommand())