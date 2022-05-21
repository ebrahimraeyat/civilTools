
from pathlib import Path

from PySide2 import QtCore


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
        from gui_civiltools import open_etabs
        etabs, filename = open_etabs.find_etabs(run=False, backup=False)
        if (
            etabs is None or
            filename is None
            ):
            return
        data, headers = etabs.get_irregularity_of_mass()
        import table_model
        table_model.show_results(data, headers, table_model.IrregularityOfMassModel)
        
    def IsActive(self):
        return True


        