
from pathlib import Path

import pandas as pd

from PySide import QtCore


class CivilIrregularityOfMass:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "Civil",
            "Irregularity Of Mass")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "Civil",
            "Irregularity Of Mass")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "mass.svg"
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
        data, headers = etabs.get_irregularity_of_mass()
        df = pd.DataFrame(data, columns=headers)
        import table_model
        table_model.show_results(df, table_model.IrregularityOfMassModel,
                                 etabs=etabs,
                                 json_file_name=f"IrregularityOfMass {etabs.get_file_name_without_suffix()}",
                                 )
        
    def IsActive(self):
        return True


        