
from pathlib import Path

from PySide import QtCore
from PySide.QtGui import QMessageBox

import FreeCADGui as Gui

import table_model
from qt_models.columns_pmm_model import ColumnsPMMAll, ColumnsPMMDelegate



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
        df = etabs.design.get_concrete_columns_pmm_table()
        column_names = etabs.frame_obj.concrete_section_names('Column')
        kwargs = {
            'etabs': etabs,
            'custom_delegate': ColumnsPMMDelegate,
            'sections': column_names,
            }
        table_model.show_results(
            df,
            model=ColumnsPMMAll,
            function=etabs.view.show_frame_with_lable_and_story,
            json_file_name="columns_pmm_ratios",
            etabs=etabs,
            kwargs=kwargs,
            )
        
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