from pathlib import Path
import csv

from PySide2 import  QtWidgets
from PySide2 import QtCore

import FreeCAD
import FreeCADGui as Gui

from db import ostanha
from exporter import civiltools_config
from qt_models import treeview_system

from building.build import StructureSystem, Building

civiltools_path = Path(__file__).absolute().parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_model):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'civiltools_project_settings.ui'))
        self.etabs = etabs_model
        self.stories = self.etabs.SapModel.Story.GetStories()[1]
        self.set_system_treeview()
        self.fill_cities()
        self.create_connections()
        self.fill_top_bot_stories()
        self.fill_load_cases()
        self.load_config()
        # self.fill_height_and_no_of_stories()

    def fill_load_cases(self):
        load_patterns = self.etabs.load_patterns.get_load_patterns()
        map_number_to_pattern = {
            1 : self.form.dead_combobox,    # 'Dead',
            2 : self.form.sdead_combobox,   # 'Super Dead',
            3 : self.form.live_combobox,    # 'Live',
            4 : self.form.lred_combobox,    # 'Reducible Live',
            # 5 : self.form.dead_combobox # 'Seismic',
            # 6 : self.form.dead_combobox # 'Wind',
            7 : self.form.snow_combobox, # 'Snow',
            # 8 : self.form.mass_combobox, # 'Other',
            11 : self.form.lroof_combobox, # 'ROOF Live',
            # 12 : self.form.dead_combobox # 'Notional',
        }
        live_loads = [''] + [lp for lp in load_patterns if self.etabs.SapModel.LoadPatterns.GetLoadType(lp)[0] in (3, 4, 11)]
        other_loads = [''] + [lp for lp in load_patterns if self.etabs.SapModel.LoadPatterns.GetLoadType(lp)[0] == 8]
        live_loads_combobox = (
                self.form.live_combobox,
                self.form.lred_combobox,
                self.form.lroof_combobox,
                self.form.live5_combobox,
                self.form.lred5_combobox,
                self.form.live_parking_combobox,
                )
        other_combobox = (
            self.form.mass_combobox,
            self.form.ev_combobox,
            self.form.hxp_combobox,
            self.form.hxn_combobox,
            self.form.hyp_combobox,
            self.form.hyn_combobox,
            )
        for combobox in live_loads_combobox:
            combobox.addItems(live_loads)
        for combobox in other_combobox:
            combobox.addItems(other_loads)
        for lp in load_patterns:
            type_ = self.etabs.SapModel.LoadPatterns.GetLoadType(lp)[0]
            combobox = map_number_to_pattern.get(type_, None)
            i = j = -1
            if lp in live_loads:
                i = live_loads.index(lp)
            if lp in other_loads:
                j = other_loads.index(lp)
            if combobox is not None:
                if combobox in live_loads_combobox:
                    # if i == -1:
                    #     combobox.addItem(lp)
                    # else:
                    combobox.setCurrentIndex(i)
                else:
                    combobox.addItem(lp)
            if type_ == 3 and '5' in lp:
                self.form.live5_combobox.setCurrentIndex(i)
            elif type_ == 4 and '5' in lp:
                self.form.lred5_combobox.setCurrentIndex(i)
            elif type_ == 5: # seismic
                pass
            elif type_ == 8:
                if 'mass' in lp.lower() or 'wall' in lp.lower():
                    self.form.mass_combobox.setCurrentIndex(j)
                elif any((
                    'ev' in lp.lower(),
                    'ez' in lp.lower(),
                    'qv' in lp.lower(),
                    'qz' in lp.lower(),
                    )):
                    self.form.ev_combobox.setCurrentIndex(j)
        xdir, xdir_minus, xdir_plus, ydir, ydir_minus, ydir_plus = self.etabs.load_patterns.get_seismic_load_patterns()
        for combobox, name, dir_ in zip(
                (self.form.ex_combobox,
                self.form.exn_combobox,
                self.form.exp_combobox,
                self.form.ey_combobox,
                self.form.eyn_combobox,
                self.form.eyp_combobox,
                ),
                ('EX', 'EXN', 'EXP', 'EY', 'EYN', 'EYP'),
                (xdir, xdir_minus, xdir_plus, ydir, ydir_minus, ydir_plus),
            ):
            dir_.add(name)
            combobox.addItems(dir_)

    def fill_cities(self):
        ostans = ostanha.ostans.keys()
        self.form.ostan.addItems(ostans)
        self.set_citys_of_current_ostan()

    def fill_top_bot_stories(self):
        for combo_box in (
            self.form.bot_x_combo,
            self.form.top_x_combo,
            self.form.top_story_for_height,
            self.form.bot_x1_combo,
            self.form.top_x1_combo,
            self.form.top_story_for_height1,
            # self.form.bot_y_combo,
            # self.form.top_y_combo,
        ):
            combo_box.addItems(self.stories)
        n = len(self.stories)
        self.form.bot_x_combo.setCurrentIndex(0)
        self.form.top_x_combo.setCurrentIndex(n - 1)
        self.form.top_story_for_height.setCurrentIndex(n - 2)
        # self.form.bot_y_combo.setCurrentIndex(0)
        # self.form.top_y_combo.setCurrentIndex(n - 2)

    def fill_height_and_no_of_stories(self):
        if self.form.top_story_for_height_checkbox.isChecked():
            self.form.top_story_for_height.setEnabled(True)
            top_story_x = top_story_y = self.form.top_story_for_height.currentText()
        else:
            self.form.top_story_for_height.setEnabled(False)
            top_story_x = top_story_y = self.form.top_x_combo.currentText()
        bot_story_x = bot_story_y = self.form.bot_x_combo.currentText()
        # bot_story_y = self.form.bot_y_combo.currentText()
        # top_story_y = self.form.top_y_combo.currentText()
        bot_level_x, top_level_x, bot_level_y, top_level_y = self.etabs.story.get_top_bot_levels(
                bot_story_x, top_story_x, bot_story_y, top_story_y, False
                )
        hx, hy = self.etabs.story.get_heights(bot_story_x, top_story_x, bot_story_y, top_story_y, False)
        nx, ny = self.etabs.story.get_no_of_stories(bot_level_x, top_level_x, bot_level_y, top_level_y)
        self.form.no_of_story_x.setValue(nx)
        # self.form.no_story_y_spinbox.setValue(ny)
        self.form.height_x.setValue(hx)
        # self.form.height_y_spinbox.setValue(hy)
        
        # second system 
        if self.form.top_story_for_height_checkbox_1.isChecked():
            self.form.top_story_for_height1.setEnabled(True)
            top_story_x1 = top_story_y1 = self.form.top_story_for_height1.currentText()
        else:
            self.form.top_story_for_height1.setEnabled(False)
            top_story_x1 = top_story_y1 = self.form.top_x1_combo.currentText()
        bot_story_x1 = bot_story_y1 = self.form.bot_x1_combo.currentText()
        # bot_story_y = self.form.bot_y_combo.currentText()
        # top_story_y = self.form.top_y_combo.currentText()
        bot_level_x1, top_level_x1, bot_level_y1, top_level_y1 = self.etabs.story.get_top_bot_levels(
                bot_story_x1, top_story_x1, bot_story_y1, top_story_y1, False
                )
        hx, hy = self.etabs.story.get_heights(bot_story_x1, top_story_x1, bot_story_y1, top_story_y1, False)
        nx, ny = self.etabs.story.get_no_of_stories(bot_level_x1, top_level_x1, bot_level_y1, top_level_y1)
        self.form.no_of_story_x1.setValue(nx)
        # self.form.no_story_y_spinbox.setValue(ny)
        self.form.height_x1.setValue(hx)
        # self.form.height_y_spinbox.setValue(hy)

    def get_current_ostan(self):
        return self.form.ostan.currentText()

    def get_current_city(self):
        return self.form.city.currentText()

    def get_citys_of_current_ostan(self, ostan):
        '''return citys of ostan'''
        return ostanha.ostans[ostan].keys()

    def set_citys_of_current_ostan(self):
        self.form.city.clear()
        ostan = self.get_current_ostan()
        citys = self.get_citys_of_current_ostan(ostan)
        self.form.city.addItems(citys)

    def create_connections(self):
        self.form.ostan.currentIndexChanged.connect(self.set_citys_of_current_ostan)
        self.form.city.currentIndexChanged.connect(self.setA)
        self.form.bot_x_combo.currentIndexChanged.connect(self.fill_height_and_no_of_stories)
        self.form.top_x_combo.currentIndexChanged.connect(self.fill_height_and_no_of_stories)
        self.form.bot_x1_combo.currentIndexChanged.connect(self.fill_height_and_no_of_stories)
        self.form.top_x1_combo.currentIndexChanged.connect(self.fill_height_and_no_of_stories)
        self.form.save_pushbutton.clicked.connect(self.save)
        self.form.cancel_pushbutton.clicked.connect(self.reject)
        self.form.top_story_for_height_checkbox.clicked.connect(self.fill_height_and_no_of_stories)
        self.form.top_story_for_height.currentIndexChanged.connect(self.fill_height_and_no_of_stories)
        self.form.top_story_for_height_checkbox_1.clicked.connect(self.fill_height_and_no_of_stories)
        self.form.top_story_for_height1.currentIndexChanged.connect(self.fill_height_and_no_of_stories)
        self.form.activate_second_system.clicked.connect(self.second_system_clicked)
        self.form.partition_dead_checkbox.stateChanged.connect(self.partition_dead_clicked)
        self.form.partition_live_checkbox.stateChanged.connect(self.partition_live_clicked)
        # check inputs
        self.form.risk_level.currentIndexChanged.connect(self.check_inputs)
        self.form.soil_type.currentIndexChanged.connect(self.check_inputs)
        self.form.importance_factor.currentIndexChanged.connect(self.check_inputs)
        self.form.height_x.valueChanged.connect(self.check_inputs)
        self.form.no_of_story_x.valueChanged.connect(self.check_inputs)
        self.form.x_treeview.clicked.connect(self.check_inputs)
        self.form.y_treeview.clicked.connect(self.check_inputs)
        self.form.height_x1.valueChanged.connect(self.check_inputs)
        self.form.no_of_story_x1.valueChanged.connect(self.check_inputs)
        self.form.x_treeview_1.clicked.connect(self.check_inputs)
        self.form.y_treeview_1.clicked.connect(self.check_inputs)
        self.form.activate_second_system.clicked.connect(self.check_inputs)

    def partition_dead_clicked(self, checked):
        self.form.partition_live_checkbox.setChecked(not checked)
        self.form.partition_live_combobox.setEnabled(not checked)
    
    def partition_live_clicked(self, checked):
        self.form.partition_dead_checkbox.setChecked(not checked)
        self.form.partition_dead_combobox.setEnabled(not checked)

    def second_system_clicked(self, checked:bool):
        self.form.x_system_label.setEnabled(checked)
        self.form.y_system_label.setEnabled(checked)
        self.form.x_treeview_1.setEnabled(checked)
        self.form.y_treeview_1.setEnabled(checked)
        self.form.stories_for_apply_earthquake_groupox.setEnabled(checked)
        self.form.stories_for_height_groupox.setEnabled(checked)
        self.form.infill_1.setEnabled(checked)
        self.form.top_story_for_height_checkbox.setEnabled(not checked)
        if checked:
            self.form.top_story_for_height_checkbox.setChecked(not checked)
            self.form.top_story_for_height.setEnabled(not checked)
        i = self.form.top_x_combo.currentIndex()
        self.form.bot_x1_combo.setCurrentIndex(i)

    def load_config(self):
        param = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/civilTools")
        show_at_startup = param.GetBool("FirstTime", True)
        self.form.show_at_startup.setChecked(show_at_startup)
        civiltools_config.load(self.etabs, self.form)
        
    def save(self):
        ret = self.check_inputs()
        if not ret:
            return
        self.save_config()

    def save_config(self):
        tx, ty, tx1, ty1 = civiltools_config.get_analytical_periods(self.etabs)
        civiltools_config.save(self.etabs, self.form)
        civiltools_config.save_analytical_periods(self.etabs, tx, ty, tx1, ty1)
        param = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/civilTools")
        show_at_startup = self.form.show_at_startup.isChecked()
        param.SetBool("FirstTime", show_at_startup)
        ostan = self.get_current_ostan()
        city = self.get_current_city()
        param.SetString("ostan", ostan)
        param.SetString("city", city)
        self.reject()

    def reject(self):
        self.form.reject()

    def select_treeview_item(self, view, i, n):
        index = view.model().index(i, 0, QtCore.QModelIndex())
        index2 = view.model().index(n, 0, index)
        view.clearSelection()
        view.setCurrentIndex(index2)
        # view.setExpanded(index, False)
        view.setExpanded(index2, True)

    def set_system_treeview(self):
        items = {}

        # Set some random data:
        csv_path =  civiltools_path / 'db' / 'systems.csv'
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                if (
                    row[0][1] in ['ا', 'ب', 'پ', 'ت', 'ث'] or
                    row[0][0] in ['ا', 'ب', 'پ', 'ت', 'ث']
                    ):
                    i = row[0]
                    root = treeview_system.CustomNode(i)
                    items[i] = root
                else:
                    root.addChild(treeview_system.CustomNode(row))
        headers = ('System', 'Ru', 'Omega', 'Cd', 'H_max', 'alpha', 'beta', 'note', 'ID')
        self.form.x_treeview.setModel(treeview_system.CustomModel(list(items.values()), headers=headers))
        self.form.x_treeview.setColumnWidth(0, 400)
        for i in range(1,len(headers)):
            self.form.x_treeview.setColumnWidth(i, 40)
        self.form.y_treeview.setModel(treeview_system.CustomModel(list(items.values()), headers=headers))
        self.form.y_treeview.setColumnWidth(0, 400)
        for i in range(1,len(headers)):
            self.form.y_treeview.setColumnWidth(i, 40)
        # second system
        self.form.x_treeview_1.setModel(treeview_system.CustomModel(list(items.values()), headers=headers))
        self.form.x_treeview_1.setColumnWidth(0, 400)
        for i in range(1,len(headers)):
            self.form.x_treeview_1.setColumnWidth(i, 40)
        self.form.y_treeview_1.setModel(treeview_system.CustomModel(list(items.values()), headers=headers))
        self.form.y_treeview_1.setColumnWidth(0, 400)
        for i in range(1,len(headers)):
            self.form.y_treeview_1.setColumnWidth(i, 40)

    def setA(self):
        sotoh = ['خیلی زیاد', 'زیاد', 'متوسط', 'کم']
        ostan = self.get_current_ostan()
        city = self.get_current_city()
        try:
            A = int(ostanha.ostans[ostan][city][0])
            i = self.form.risk_level.findText(sotoh[A - 1])
            self.form.risk_level.setCurrentIndex(i)
        except KeyError:
            pass

    def current_building(self):
        risk_level = self.form.risk_level.currentText()
        city = self.form.city.currentText()
        soil = self.form.soil_type.currentText()
        importance_factor = float(self.form.importance_factor.currentText())
        height_x = self.form.height_x.value()
        no_of_story = self.form.no_of_story_x.value()
        is_infill = self.form.infill.isChecked()
        x_system = self.get_system(self.form.x_treeview)
        y_system = self.get_system(self.form.y_treeview)
        if x_system is None or y_system is None:
            return None, None
        build = Building(
                    risk_level,
                    importance_factor,
                    soil,
                    no_of_story,
                    height_x,
                    is_infill,
                    x_system,
                    y_system,
                    city,
                    4,
                    4,
                    )
        # Second System
        build1 = None
        if self.form.activate_second_system.isChecked():
            height_x = self.form.height_x1.value()
            if height_x == 0:
                return build, None
            no_of_story = self.form.no_of_story_x1.value()
            is_infill = self.form.infill_1.isChecked()
            x_system = self.get_system(self.form.x_treeview_1)
            y_system = self.get_system(self.form.y_treeview_1)
            if x_system is None or y_system is None:
                build1 = None
            else:
                build1 = Building(
                            risk_level,
                            importance_factor,
                            soil,
                            no_of_story,
                            height_x,
                            is_infill,
                            x_system,
                            y_system,
                            city,
                            4,
                            4,
                            )
        return build, build1

    def check_inputs(self):
        building, building1 = self.current_building()
        if building is None:
            return False
        results = building.results
        if results[0] is False:
            title, err, direction = results[1:]
            QtWidgets.QMessageBox.critical(self, "ایراد در انتخاب سیستم اول", title % direction + '\n' + str(err))
            return False
        if building1 is not None:
            results = building1.results
            if results[0] is False:
                title, err, direction = results[1:]
                QtWidgets.QMessageBox.critical(self, "ایراد در انتخاب سیستم دوم", title % direction + '\n' + str(err))
                return False
        return True

    def get_system(self, view):
        ret = civiltools_config.get_treeview_item_prop(view)
        if ret is None:
            return
        system, lateral, *args = ret
        if 'x' in view.objectName():
            system = StructureSystem(system, lateral, 'X')
        elif 'y' in view.objectName():
            system = StructureSystem(system, lateral, 'Y')
        return system

