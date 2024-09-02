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
        self.form.standard_rebars_groupbox.clicked.connect(self.rebar_group_clicked)
        self.form.other_rebars_groupbox.clicked.connect(self.rebar_group_clicked)
        self.form.s340_checkbox.clicked.connect(self.standard_rebar_clicked)
        self.form.s400_checkbox.clicked.connect(self.standard_rebar_clicked)
        self.form.s420_checkbox.clicked.connect(self.standard_rebar_clicked)
        self.form.s500_checkbox.clicked.connect(self.standard_rebar_clicked)

    def standard_rebar_clicked(self, check):
        sender = self.sender()
        name = sender.objectName()
        fy = name[1:4]
        exec(f"self.form.s{fy}fy_spinbox.setEnabled(check)")
        exec(f"self.form.s{fy}fu_spinbox.setEnabled(check)")
        exec(f"self.form.s{fy}_name.setEnabled(check)")

    def rebar_group_clicked(self, check):
        sender = self.sender()
        if sender == self.form.standard_rebars_groupbox:
            self.form.other_rebars_groupbox.setChecked(not check)
        elif sender == self.form.other_rebars_groupbox:
            self.form.standard_rebars_groupbox.setChecked(not check)

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
        tab_index = self.form.tabWidget.currentIndex()
        if tab_index == 0:
            name = self.form.fc_name.text()
            fc = self.form.fc_spinbox.value()
            if self.form.ec1.isChecked():
                weight_for_calculate_ec = self.form.wc.value()
            else:
                weight_for_calculate_ec = 0
            self.etabs.material.add_concrete(name, fc, weight_for_calculate_ec=weight_for_calculate_ec)
            QtWidgets.QMessageBox.information(None, "Done", f"The Concrete {name} with f'c={fc} MPa added to model.")
        elif tab_index == 1: # rebars
            add_standards = self.form.standard_rebars_groupbox.isChecked()
            add_others = self.form.other_rebars_groupbox.isChecked()
            if not add_standards and not add_others:
                QtWidgets.QMessageBox.warning(None, "Selection", "Please select atleast one rebar to create!")
                return
            rebar_names = []
            if add_standards:
                checkboxes = (self.form.s340_checkbox, self.form.s400_checkbox, self.form.s420_checkbox, self.form.s500_checkbox)
                fys = (self.form.s340fy_spinbox, self.form.s400fy_spinbox, self.form.s420fy_spinbox, self.form.s500fy_spinbox)
                fus = (self.form.s340fu_spinbox, self.form.s400fu_spinbox, self.form.s420fu_spinbox, self.form.s500fu_spinbox)
                names = (self.form.s340_name, self.form.s400_name, self.form.s420_name, self.form.s500_name)
                for i, checkbox in enumerate(checkboxes):
                    if checkbox.isChecked:
                        fy = fys[i].value()
                        fu = fus[i].value()
                        name = names[i].text()
                        self.etabs.material.add_rebar(name, fy, fu)
                        rebar_names.append(name)
            if add_others:
                fy = self.form.other_fy_spinbox.value()
                fu = self.form.other_fu_spinbox.value()
                name = self.form.other_name.text()
                self.etabs.material.add_rebar(name, fy, fu)
                rebar_names.append(name)
            QtWidgets.QMessageBox.information(None, "Done", f"The {', '.join(rebar_names)} rebar/s added to model.")


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