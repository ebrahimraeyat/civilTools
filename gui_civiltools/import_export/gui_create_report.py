
from pathlib import Path

from PySide2 import QtCore, QtWidgets
# from PySide2.QtWidgets import QMessageBox

import FreeCADGui as Gui

import python_functions



class CiviltoolsCreateReport:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Create Report")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Create a word document report")
        path = str(
                   Path(__file__).parent.absolute().parent.parent / "images" / "word.svg"
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
        from exporter import civiltools_config, export_to_word
        # d = etabs.get_settings_from_model()
        d = civiltools_config.get_settings_from_etabs(etabs)
        if len(d) == 0:
            QtWidgets.QMessageBox.warning(None, 'Settings', 'Please Set Options First!')
            Gui.runCommand("civiltools_settings")
        if len(d) == 0:
            return
        build = civiltools_config.current_building_from_config(d)
        from report import all_report as report
        doc = report.create_doc(table_of_content=True)
        doc = export_to_word.export(build, doc=doc)
        doc, doc_file = report.create_report(etabs=etabs, doc=doc)
        python_functions.open_file(doc_file)
        # doc.save(str(filename))
        
        
    def IsActive(self):
        return True
    
Gui.addCommand("civiltools_create_report", CiviltoolsCreateReport())
        