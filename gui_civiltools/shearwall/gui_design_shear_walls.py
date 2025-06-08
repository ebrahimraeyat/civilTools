
from pathlib import Path

from PySide2 import QtCore
from PySide2.QtWidgets import QMessageBox

import FreeCADGui as Gui

import table_model
from qt_models.shear_wall_ratio_model import ShearWallsRatio



class CivilToolsDesignShearWalls:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Start Design")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Design Shear Walls and Shows the Ratios.")
        path = str(
                   Path(__file__).parent.absolute().parent.parent / "images" / "shear_wall" / "design_shear_wall.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        import find_etabs
        etabs, filename = find_etabs.find_etabs(run=False, backup=True)
        if (
            etabs is None or
            filename is None
            ):
            return
        df = etabs.shearwall.get_wall_ratios()
        table_model.show_results(
            df,
            model=ShearWallsRatio,
            function=etabs.view.show_areas_and_frames_with_pier_and_story,
            json_file_name="shear_walls_ratios",
            )
        # show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True


Gui.addCommand("civilTools_design_shear_walls", CivilToolsDesignShearWalls())