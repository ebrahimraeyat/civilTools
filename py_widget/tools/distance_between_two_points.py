from pathlib import Path
from PySide import QtGui
from PySide.QtGui import QMessageBox
import FreeCADGui as Gui

import civiltools_rc

civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtGui.QWidget):
    def __init__(self, etabs_model):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'tools' / 'distance_between_two_points.ui'))
        self.etabs = etabs_model
        self.create_connections()
        self.calculate()

    def create_connections(self):
        self.form.show_button.clicked.connect(self.show_points)
        self.form.calculate.clicked.connect(self.calculate)

    
    def show_points(self):
        if self.form.point_list.count() < 2:
            return
        p1 = self.form.point_list.item(0).text()
        p2 = self.form.point_list.item(1).text()
        self.etabs.SapModel.SelectObj.ClearSelection()
        self.etabs.SapModel.PointObj.SetSelected(p1, True)
        self.etabs.SapModel.PointObj.SetSelected(p2, True)
        self.etabs.SapModel.View.RefreshView()

    def fill_points(self):
        points_names = self.etabs.select_obj.get_selected_obj_type(1)
        line_name = self.etabs.select_obj.get_selected_obj_type(2)
        if points_names is None and line_name is None:
            message = 'Please Select Two Points or a Frame in ETBAS Model.'
            QMessageBox.information(None, 'Selection', message)
            return
        if len(points_names) < 2 and not line_name:
            return
        if len(points_names) > 1:
            p1, p2 = points_names[:2]
        else:
            p1, p2, _ = self.etabs.SapModel.FrameObj.GetPoints(line_name[0])
        self.form.point_list.clear()
        self.form.point_list.addItems([p1, p2])
        return True

    def calculate(self):
        ret = self.fill_points()
        if ret is None:
            return
        p1 = self.form.point_list.item(0).text()
        p2 = self.form.point_list.item(1).text()
        self.etabs.set_current_unit('N', 'm')
        dx, dy, dz, distance = self.etabs.points.get_distance_between_two_points(p1, p2)
        self.form.dist.setValue(distance)
        self.form.dx.setValue(dx)
        self.form.dy.setValue(dy)
        self.form.dz.setValue(dz)
        self.etabs.SapModel.SelectObj.ClearSelection()
        self.etabs.SapModel.View.RefreshView()


