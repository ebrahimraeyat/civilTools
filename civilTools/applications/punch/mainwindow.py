from PyQt5 import uic, QtWidgets
import sys
from punch import Column, Foundation, Punch

 
class Ui(QtWidgets.QMainWindow):

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('mainwindow.ui', self)
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
        
    def calculate_Vc(self):
        curr_column = self.get_column()
        curr_foundation = self.get_foundation()
        punch = Punch(curr_foundation, curr_column)
        return punch.calculate_Vc()

    def update_result(self):
        Vc = self.calculate_Vc()
        text = 'Vc = {:0.0f} \tKn'.format(Vc/1000)
        self.plainTextEdit.setPlainText(text)


 
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(app.exec_())