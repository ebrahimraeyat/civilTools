from pathlib import Path
import time

from PySide2.QtWidgets import QMessageBox

import FreeCADGui as Gui
import FreeCAD

# Import the function to get executable paths
# import find_and_register_softwares as far

class CivilToolsConnectToSoftware:

    def GetResources(self):
        # Get the last saved software path from FreeCAD parameters
        return {
            'Pixmap': str(Path(__file__).parent.parent / "images" / 'general' / 'connect.svg'),
            'MenuText': "Connect to Software",
            'ToolTip': "Connect to ETABS, SAP2000, or SAFE software",
        }

    def Activated(self):
        
        from py_widget.connect_to_software import Form
        win = Form()
        win.form.exec_()
        if win.require_restart:
            import freecad_funcs
            freecad_funcs.restart_freecad(check_test=False)
        Gui.getMainWindow().statusBar().showMessage(f"Connected to {win.title}")

    def IsActive(self):
        return True


# Register the command in FreeCAD
Gui.addCommand('civiltools_connect_to_software', CivilToolsConnectToSoftware())