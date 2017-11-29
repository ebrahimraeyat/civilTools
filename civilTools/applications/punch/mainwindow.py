from PyQt5 import uic, QtWidgets, QtCore
import sys
from .punch import Column, Foundation, Punch, ShearSteel

 
class Ui(QtWidgets.QMainWindow):

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('applications/punch/mainwindow.ui', self)
        self.run_Button.clicked.connect(self.update_result)

    def get_column(self):
        c1 = self.c1_spinBox.value()
        c2 = self.c2_spinBox.value()
        pos = self.pos_comboBox.currentText()
        return Column(shap='rec', pos=pos, c1=c1, c2=c2)
        

    def get_foundation(self):
        fc = self.fc_spinBox.value()
        dl = int(self.dl_comboBox.currentText())
        ds = int(self.ds_comboBox.currentText())
        cover = self.cover_spinBox.value()
        height = self.height_spinBox.value()
        return Foundation(fc, height, dl, ds, cover)

    def get_punch(self):
        curr_column = self.get_column()
        curr_foundation = self.get_foundation()
        if self.b0_groupBox.isChecked():
            b0 = self.b0_spinBox.value()
            return Punch(curr_foundation, curr_column, b0=b0)
        return Punch(curr_foundation, curr_column)
        
    def calculate_punch(self):
        punch = self.get_punch()
        punch.calculate_Vc()
        return punch

    def get_shear_steel(self):
        curr_column = self.get_column()
        curr_foundation = self.get_foundation()
        b0 = None
        if self.b0_groupBox.isChecked():
            b0 = self.b0_spinBox.value()
        Vu = self.vu_spinBox.value()
        fys = int(self.fys_comboBox.currentText())
        ds = int(self.ds_punch_comboBox.currentText())
        return ShearSteel(curr_foundation, curr_column, Vu=Vu, b0=b0, fy=fys, rebar=ds)

    def calculate_shear_Vc(self):
        shear_steel = self.get_shear_steel()
        shear_steel.calculate_Vc()
        return shear_steel

    def update_result(self):
        if self.shear_groupBox.isChecked():
            result = self.calculate_shear_Vc()
        else:
            result = self.calculate_punch()
        self.plainTextEdit.setPlainText(result.__str__())


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    translator = QtCore.QTranslator()
    translator.load("applications/punch/mainwindow.qm")
    app.installTranslator(translator)
    window = Ui()
    window.show()
    sys.exit(app.exec_())