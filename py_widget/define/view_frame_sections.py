from pathlib import Path

from PySide2 import  QtWidgets

import FreeCAD
import FreeCADGui as Gui

import civiltools_rc


civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'define' / 'view_frame_sections.ui'))
        self.create_connections()

    def create_connections(self):
        self.form.columns_tableview.clicked.connect(self.view_section)

    def view_section(self):
        row = self.form.columns_tableview.currentIndex().row()
        section = self.model.sections[row]
        for obj in FreeCAD.ActiveDocument.Objects:
            if hasattr(obj, 'Proxy') and hasattr(obj.Proxy, 'Type') and obj.Proxy.Type == "ConcreteColumnSection":
                if obj.Section_Name == section.Section_Name:
                   obj.ViewObject.show()
                else:
                    obj.ViewObject.hide()
        
    def reject(self):
        Gui.Control.closeDialog()