from pathlib import Path


from PySide2 import  QtWidgets
import FreeCADGui as Gui
import FreeCAD
import civiltools_rc

civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    LOADTYPE = {'Force' : 1, 'Moment': 2}
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

    def reset_widget(self):
        if self.form.auto_height.isChecked():
            self.form.none_beam_h.setEnabled(True)
            self.form.user_height.setEnabled(False)
        elif self.form.override_height.isChecked():
            self.form.none_beam_h.setEnabled(False)
            self.form.user_height.setEnabled(True)

    def assign(self):
        loadpat = self.form.loadpat.currentText()
        mass_per_area = self.form.mass.value()
        if self.form.override_height.isChecked():
            height = self.form.user_height.value() * 1000
        else:
            height = None
        stories = [item.text() for item in self.form.stories.selectedItems()]
        none_beam_h = self.form.none_beam_h.value()
        dist1 = self.form.dist1.value()
        dist2 = self.form.dist2.value()
        relative = self.form.relative.isChecked()
        load_type = Form.LOADTYPE[self.form.load_type.currentText()]
        replace = self.form.replace.isChecked()
        parapet_wall_height = self.form.parapet_wall_height.value()
        height_from_below = self.form.height_from_below.isChecked()
        opening_ratio = self.form.opening_ratio.value()
        names = None
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
                labels=names,
                stories=stories,
                relative=relative,
                replace=replace,
                # item_type,
                height=height,
                none_beam_h=none_beam_h,
                parapet=f'{parapet_wall_height} m',
                # height_from_below,
                opening_ratio=opening_ratio,
            )
        elif self.form.etabs_from_freecad_button.isChecked():
            from freecad_py.assign import wall_loads
            wall_loads.assign_wall_loads_to_etabs(self.etabs)


    def reject(self):
        Gui.Control.closeDialog()