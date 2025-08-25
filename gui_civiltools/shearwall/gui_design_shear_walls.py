
from pathlib import Path

from PySide import QtCore
from PySide.QtGui import QMessageBox

import FreeCADGui as Gui
import FreeCAD

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
        p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/civilTools")
        char_len = int(p.GetFloat('table_max_etabs_model_name_length', 200))
        table_model.show_results(
            df,
            model=ShearWallsRatio,
            function=etabs.view.show_areas_and_frames_with_pier_and_story,
            json_file_name=f"shear_walls_ratios {etabs.get_file_name_without_suffix()[:char_len]}",
            )
        # show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True


Gui.addCommand("civilTools_design_shear_walls", CivilToolsDesignShearWalls())