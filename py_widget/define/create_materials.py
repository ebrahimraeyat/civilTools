from pathlib import Path

from PySide2 import  QtWidgets

import FreeCADGui as Gui


civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self,
        etabs_model,
        ):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'define' / 'create_materials.ui'))
        self.etabs = etabs_model
        self.create_connections()

    def create_connections(self):
        self.form.create_pushbutton.clicked.connect(self.create_materials)
        self.form.ec1.clicked.connect(self.ec_clicked)
        self.form.ec2.clicked.connect(self.ec_clicked)
        self.form.fc_spinbox.valueChanged.connect(self.set_fc_name)

    def set_fc_name(self, value):
        self.form.fc_name.setText(f"C{value}")
    
    def ec_clicked(self, check):
        sender = self.sender()
        if sender == self.form.ec1:
            self.form.wc.setEnabled(check)
        elif sender == self.form.ec2:
            self.form.wc.setEnabled(not check)

    def create_materials(self):
        if self.etabs.SapModel.GetModelIsLocked():
            if QtWidgets.QMessageBox.question(
                None,
                "Unlock Model?",
                "The model is lock, do you want to unlock model?",
                ) == QtWidgets.QMessageBox.No:
                return
            self.etabs.unlock_model()
        name = self.form.fc_name.text()
        fc = self.form.fc_spinbox.value()
        if self.form.ec1.isChecked():
            weight_for_calculate_ec = self.form.wc.value()
        else:
            weight_for_calculate_ec = 0
        self.etabs.material.add_concrete(name, fc, weight_for_calculate_ec=weight_for_calculate_ec)
        QtWidgets.QMessageBox.information(None, "Done", f"The Concrete {name} with f'c={fc} MPa added to model.")

    def reject(self):
        self.form.reject()

    
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    sys.path.insert(0, r"C:\Users\ebrahim\AppData\Roaming\FreeCAD\Mod\etabs_api")
    import find_etabs
    etabs, filename = find_etabs.find_etabs(run=False, backup=False)
    if not (
        etabs is None or
        filename is None
        ):
        
        mytree = Form(etabs)
        mytree.show()
        sys.exit(app.exec_())