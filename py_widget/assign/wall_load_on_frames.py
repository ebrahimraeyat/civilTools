from pathlib import Path


from PySide2 import  QtWidgets
from PySide2.QtWidgets import QMessageBox
from PySide2.QtGui import QIcon


import FreeCADGui as Gui
import FreeCAD
import civiltools_rc

civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    # LOADTYPE = {'Force' : 1, 'Moment': 2}
    def __init__(self, etabs_model):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'assign' / 'wall_load_on_frames.ui'))
        self.etabs = etabs_model
        self.fill_widget()
        self.create_connections()

    def fill_widget(self):
        stories = None
        load_patterns = None
        if hasattr(self.etabs, 'SapModel'):
            stories = self.etabs.SapModel.Story.GetNameList()[1]
            load_patterns = self.etabs.load_patterns.get_load_patterns()
        elif FreeCAD.ActiveDocument:
            for obj in FreeCAD.ActiveDocument.Objects:
                if hasattr(obj, 'IfcType') and obj.IfcType == 'Building':
                    if hasattr(obj, 'Dead'):
                        load_patterns = obj.Dead
                    outlists = obj.OutList
                    stories = []
                    for o in outlists:
                        if hasattr(o, 'IfcType') and o.IfcType == 'Building Storey':
                            stories.append(o.Label)
                    self.form.freecad_button.setChecked(True)
                    self.form.etabs_button.setChecked(False)
        if stories is not None:
            self.form.stories.addItems(stories)
            self.select_all_stories()
        if load_patterns is not None:
            self.form.loadpat.addItems(load_patterns)

    def select_all_stories(self):
        for i in range(self.form.stories.count()):
            item = self.form.stories.item(i)
            item.setSelected(True)

    def create_connections(self):
        self.form.auto_height.clicked.connect(self.reset_widget)
        self.form.override_height.clicked.connect(self.reset_widget)
        self.form.relative.clicked.connect(self.set_dists_range)
        self.form.assign_button.clicked.connect(self.assign)
        self.form.cancel_button.clicked.connect(self.reject)
        self.form.refresh_button.clicked.connect(self.refresh_clicked)
        self.form.interior_wall_radiobutton.clicked.connect(self.wall_type_clicked)
        self.form.facade_wall_radiobutton.clicked.connect(self.wall_type_clicked)
        self.form.etabs_button.clicked.connect(self.apply_type_clicked)
        self.form.freecad_button.clicked.connect(self.apply_type_clicked)
        self.form.etabs_from_freecad_button.clicked.connect(self.apply_type_clicked)

    def apply_type_clicked(self, check):
        sender = self.sender()
        if sender == self.form.etabs_button:
            self.form.get_from_etabs_draw_on_freecad.setEnabled(not check)
            self.form.selected_wall.setEnabled(not check)
            self.form.assign_button.setIcon(QIcon(':/civiltools/images/etabs.png'))
        if sender == self.form.freecad_button:
            self.form.get_from_etabs_draw_on_freecad.setEnabled(check)
            self.form.selected_wall.setEnabled(not check)
            self.form.assign_button.setIcon(QIcon(':/civiltools/images/freecad.svg'))
        if sender == self.form.etabs_from_freecad_button:
            self.form.get_from_etabs_draw_on_freecad.setEnabled(not check)
            self.form.selected_wall.setEnabled(check)
            self.form.assign_button.setIcon(QIcon(':/civiltools/images/etabs.png'))

    def wall_type_clicked(self, check):
        sender = self.sender()
        if sender == self.form.interior_wall_radiobutton:
            self.form.mass.setEnabled(check)
            self.form.facade_wall_mass.setEnabled(not check)
            self.form.opening_label.setEnabled(not check)
            self.form.opening_ratio.setEnabled(not check)
        elif sender == self.form.facade_wall_radiobutton:
            self.form.mass.setEnabled(not check)
            self.form.facade_wall_mass.setEnabled(check)
            self.form.opening_label.setEnabled(check)
            self.form.opening_ratio.setEnabled(check)

    def refresh_clicked(self):
        selected_objects = self.etabs.select_obj.get_selected_objects()
        frames = selected_objects.get(2, None)
        if frames is None:
            QMessageBox.warning(None, 'Selection', "Please select one Beam")
            return
        beams = []
        for frame in frames:
            if self.etabs.frame_obj.is_beam(frame):
                beams.append(frame)
        if not beams:
            QMessageBox.warning(None, 'Selection', "Please select one Beam")
            return
        if len(beams) > 1:
            QMessageBox.warning(None, 'Selection', "Please select one Beam only")
            return
        beam = beams[0]
        points = selected_objects.get(1, None)
        if points is None:
            QMessageBox.warning(None, 'Selection', "Please select two points")
            return
        elif len(points) != 2:
            QMessageBox.warning(None, 'Selection', "Please exactly select two points")
            return
        p1_sel, p2_sel = points
        p1, p2, _ = self.etabs.SapModel.FrameObj.GetPoints(beam)
        d1 = self.etabs.points.get_distance_between_two_points_in_XY(p1, p1_sel)
        d2 = self.etabs.points.get_distance_between_two_points_in_XY(p1, p2_sel)
        if d2 < d1:
            p1_sel, p2_sel = p2_sel, p1_sel
        beam_length = self.etabs.points.get_distance_between_two_points_in_XY(p1, p2)
        dist1 = min(d1 / beam_length, 1)
        dist2 = min(d2 / beam_length, 1)
        self.form.relative.setChecked(True)
        self.form.dist1.setValue(dist1)
        self.form.dist2.setValue(dist2)

    def getStandardButtons(self):
        return 0

    def set_dists_range(self):
        if self.form.relative.isChecked():
            self.form.dist1.setRange(0, 1)
            self.form.dist2.setRange(0, 1)
            self.form.dist1.setSuffix('')
            self.form.dist2.setSuffix('')
        else:
            self.form.dist1.setRange(0, 30)
            self.form.dist2.setRange(0, 30)
            self.form.dist1.setSuffix(' m')
            self.form.dist2.setSuffix(' m')

    def reset_widget(self, check):
        sender = self.sender()
        if sender == self.form.auto_height:
            self.form.none_beam_h.setEnabled(check)
            self.form.none_beam_label.setEnabled(check)
            self.form.parapet_wall_height_label.setEnabled(check)
            self.form.parapet_wall_height.setEnabled(check)
            self.form.user_height.setEnabled(not check)
        elif sender == self.form.override_height:
            self.form.none_beam_h.setEnabled(not check)
            self.form.none_beam_label.setEnabled(not check)
            self.form.parapet_wall_height_label.setEnabled(not check)
            self.form.parapet_wall_height.setEnabled(not check)
            self.form.user_height.setEnabled(check)

    def assign(self):
        loadpat = self.form.loadpat.currentText()
        if self.form.interior_wall_radiobutton.isChecked():
            mass_per_area = self.form.mass.value()
            opening_ratio = 0
        elif self.form.facade_wall_radiobutton.isChecked():
            mass_per_area = self.form.facade_wall_mass.value()
            opening_ratio = self.form.opening_ratio.value()
        if self.form.override_height.isChecked():
            if self.form.etabs_button.isChecked():
                height = self.form.user_height.value()
            elif self.form.freecad_button.isChecked():
                height = self.form.user_height.value() * 1000
        else:
            height = None
        stories = [item.text() for item in self.form.stories.selectedItems()]
        none_beam_h = self.form.none_beam_h.value()
        dist1 = self.form.dist1.value()
        dist2 = self.form.dist2.value()
        relative = self.form.relative.isChecked()
        load_type = 1
        replace = self.form.replace.isChecked()
        parapet_wall_height = self.form.parapet_wall_height.value()
        height_from_below = self.form.height_from_below.isChecked()
        names = labels = None
        if self.form.get_from_etabs_draw_on_freecad.isChecked():
            names = []
            labels = []
            try:
                types, all_names = self.etabs.SapModel.SelectObj.GetSelected()[1:3]
            except IndexError:
                types, all_names = [], []
            for t, name in zip(types, all_names):
                if t == 2 and self.etabs.frame_obj.is_beam(name):
                    names.append(name)
                    label = self.etabs.SapModel.FrameObj.GetLabelFromName(name)[0]
                    labels.append(label)
            if not labels:
                labels = None
            if not names:
                names = None
            print(names)
            print(labels)
        item_type = 0
        if self.form.etabs_button.isChecked():
            self.etabs.frame_obj.assign_gravity_load_to_selfs_and_above_beams(
                loadpat,
                mass_per_area,
                dist1,
                dist2,
                names,
                stories,
                load_type,
                relative,
                replace,
                item_type,
                height,
                none_beam_h,
                parapet_wall_height,
                height_from_below,
                opening_ratio,
            )
        elif self.form.freecad_button.isChecked():
            from freecad_py.assign import wall_loads
            wall_loads.add_wall_on_beams(
                loadpat=loadpat,
                mass_per_area=mass_per_area,
                dist1=dist1,
                dist2=dist2,
                labels=labels,
                stories=stories,
                relative=relative,
                replace=replace,
                # item_type,
                height=height,
                none_beam_h=none_beam_h * 1000,
                parapet=f'{parapet_wall_height} m',
                # height_from_below,
                opening_ratio=opening_ratio,
            )
        elif self.form.etabs_from_freecad_button.isChecked():
            if self.form.selected_wall.isChecked():
                walls = Gui.Selection.getSelection()
            else:
                walls = []
            self.etabs.frame_obj.assign_wall_loads_to_etabs(
                walls=walls,
                )
            QMessageBox.information(None, 'Applied', 'Wall loads applied in ETABS Model.')

    def reject(self):
        Gui.Control.closeDialog()