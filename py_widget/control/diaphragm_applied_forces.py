from pathlib import Path

from PySide2 import  QtWidgets
import FreeCADGui as Gui
import civiltools_rc

from exporter import civiltools_config

civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_model, d):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'control' / 'diaphragm_applied_forces.ui'))
        self.etabs = etabs_model
        self.d = civiltools_config.load(self.etabs, self.form, d, reverse=True, include_base=False)
        self.set_omega()
        self.create_connections()

    def create_connections(self):
        self.form.create_pushbutton.clicked.connect(self.create)
        # self.form.cancel_button.clicked.connect(self.reject)

    def set_omega(self):
        building = civiltools_config.current_building_from_config(self.d)
        x_amplified_earthquakes = building.x_system.phi0
        y_amplified_earthquakes = building.y_system.phi0
        self.form.omega_x.setValue(x_amplified_earthquakes)
        self.form.omega_y.setValue(y_amplified_earthquakes)


    def create(self):
        self.etabs.unlock_model()
        risk_level = self.form.risk_level.currentText()
        sa = get_acc(risk_level)
        importance_factor = float(self.form.importance_factor.currentText())
        ai = sa * importance_factor
        if self.form.collector_groupbox.isChecked():
            x_amplified_earthquakes = self.form.omega_x.value()
            y_amplified_earthquakes = self.form.omega_y.value()
        elif any((
            self.form.reentrance_corner_checkbox.isChecked(),
            self.form.diaphragm_discontinuity_checkbox.isChecked(),
            self.form.out_of_plane_offset_checkbox.isChecked(),
            sa > 0.2 and self.form.in_plane_discontinuity_checkbox.isChecked(),
        )):
           x_amplified_earthquakes = 1.25
           y_amplified_earthquakes = 1.25
        else:
            x_amplified_earthquakes = 1  
            y_amplified_earthquakes = 1  
        stories = [item.text() for item in self.form.stories.selectedItems()]
        self.etabs.story.create_files_diaphragm_applied_forces(
                                        stories=stories,
                                        x_amplified_earthquakes=x_amplified_earthquakes,
                                        y_amplified_earthquakes=y_amplified_earthquakes,
                                        d=self.d,
                                        ai=ai,
        )
        self.form.close()

    def getStandardButtons(self):
        return 0
    
def get_acc(sath):
        sotoh = {'خیلی زیاد' : 0.35,
                'زیاد' : 0.30,
                'متوسط' : 0.25,
                'کم' : 0.20,
                }
        return sotoh[sath]
