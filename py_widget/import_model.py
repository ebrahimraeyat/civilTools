from pathlib import Path

from PySide2 import  QtWidgets
import FreeCADGui as Gui

import civiltools_rc


civiltools_path = Path(__file__).absolute().parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_obj):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'import_model.ui'))
        self.etabs = etabs_obj
        self.form.import_button.clicked.connect(self.start_import)

    def start_import(self):
        import_beams = self.form.beams.isChecked()
        import_columns = self.form.columns.isChecked()
        import_braces = self.form.braces.isChecked()
        import_floors = self.form.floors.isChecked()
        import_walls = self.form.walls.isChecked()
        import_openings = self.form.openings.isChecked()
        new_model = self.form.new_model.isChecked()
        import import_model
        import_model.import_model(
            etabs=self.etabs,
            import_beams=import_beams,
            import_columns=import_columns,
            import_braces=import_braces,
            import_floors=import_floors,
            import_walls=import_walls,
            import_openings=import_openings,
            new_model=new_model,
            )
        Gui.SendMsgToActiveView("ViewFit")
        Gui.activeDocument().activeView().viewIsometric()
        Gui.runCommand('Std_PerspectiveCamera',1)

    def reject(self):
        import FreeCADGui as Gui
        Gui.Control.closeDialog()

    
