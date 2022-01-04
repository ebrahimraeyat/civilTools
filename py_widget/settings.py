import os
from pathlib import Path

from PySide2 import  QtWidgets
from PySide2.QtWidgets import QTreeWidgetItemIterator

import FreeCAD
import FreeCADGui as Gui

from db import ostanha
from exporter import config

civiltools_path = Path(__file__).absolute().parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_model):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'civiltools_project_settings.ui'))
        self.etabs = etabs_model
        self.stories = self.etabs.SapModel.Story.GetStories()[1]
        self.create_widgets()
        self.create_connections()
        self.fill_top_bot_stories()
        self.fill_height_and_no_of_stories()
        self.load_config()

    def create_widgets(self):
        ostans = ostanha.ostans.keys()
        self.form.ostanBox.addItems(ostans)
        self.set_citys_of_current_ostan()
        # self.setA()
        iterator = QTreeWidgetItemIterator(self.form.x_treeWidget)
        i = 0
        while iterator.value():
            item = iterator.value()
            iterator += 1
            if i == 2:
                self.form.x_treeWidget.setCurrentItem(item, 0)
                break
            i += 1
        iterator = QTreeWidgetItemIterator(self.form.y_treeWidget)
        i = 0
        while iterator.value():
            item = iterator.value()
            iterator += 1
            if i == 2:
                self.form.y_treeWidget.setCurrentItem(item, 0)
                break
            i += 1

    def fill_top_bot_stories(self):
        for combo_box in (
            self.form.bot_x_combo,
            self.form.top_x_combo,
            # self.form.bot_y_combo,
            # self.form.top_y_combo,
        ):
            combo_box.addItems(self.stories)
        n = len(self.stories)
        self.form.bot_x_combo.setCurrentIndex(0)
        self.form.top_x_combo.setCurrentIndex(n - 2)
        # self.form.bot_y_combo.setCurrentIndex(0)
        # self.form.top_y_combo.setCurrentIndex(n - 2)

    def fill_height_and_no_of_stories(self):
        bot_story_x = bot_story_y = self.form.bot_x_combo.currentText()
        top_story_x = top_story_y = self.form.top_x_combo.currentText()
        # bot_story_y = self.form.bot_y_combo.currentText()
        # top_story_y = self.form.top_y_combo.currentText()
        bot_level_x, top_level_x, bot_level_y, top_level_y = self.etabs.story.get_top_bot_levels(
                bot_story_x, top_story_x, bot_story_y, top_story_y, False
                )
        hx, hy = self.etabs.story.get_heights(bot_story_x, top_story_x, bot_story_y, top_story_y, False)
        nx, ny = self.etabs.story.get_no_of_stories(bot_level_x, top_level_x, bot_level_y, top_level_y)
        self.form.no_story_x_spinbox.setValue(nx)
        # self.form.no_story_y_spinbox.setValue(ny)
        self.form.height_x_spinbox.setValue(hx)
        # self.form.height_y_spinbox.setValue(hy)

    def get_current_ostan(self):
        return self.form.ostanBox.currentText()

    def get_current_city(self):
        return self.form.cityBox.currentText()

    def get_citys_of_current_ostan(self, ostan):
        '''return citys of ostan'''
        return ostanha.ostans[ostan].keys()

    def set_citys_of_current_ostan(self):
        self.form.cityBox.clear()
        ostan = self.get_current_ostan()
        citys = self.get_citys_of_current_ostan(ostan)
        # citys.sort()
        self.form.cityBox.addItems(citys)

    def create_connections(self):
        self.form.ostanBox.currentIndexChanged.connect(self.set_citys_of_current_ostan)
        self.form.cityBox.currentIndexChanged.connect(self.setA)
        self.form.x_treeWidget.itemActivated.connect(self.xactivate)
        self.form.bot_x_combo.currentIndexChanged.connect(self.fill_height_and_no_of_stories)
        self.form.top_x_combo.currentIndexChanged.connect(self.fill_height_and_no_of_stories)

    def accept(self):
        self.save_config()
        Gui.Control.closeDialog()

    def load_config(self):
        etabs_filename = self.etabs.get_filename()
        json_file = etabs_filename.with_suffix('.json')
        if json_file.exists():
            config.load(json_file, self.form)
        param = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/civilTools")
        show_at_startup = param.GetBool("FirstTime", True)
        self.form.show_at_startup.setChecked(show_at_startup)
        ostan = param.GetString("ostan", 'قم')
        city = param.GetString("city", 'قم')
        index = self.form.ostanBox.findText(ostan)
        self.form.ostanBox.setCurrentIndex(index)
        index = self.form.cityBox.findText(city)
        self.form.cityBox.setCurrentIndex(index)

    def save_config(self, json_file=None):
        exists = False
        if not json_file:
            etabs_filename = self.etabs.get_filename()
            json_file = etabs_filename.with_suffix('.json')
        if json_file.exists():
            exists = True
            tx, ty = config.get_analytical_periods(json_file)
        config.save(json_file, self.form)
        if exists:
            config.save_analytical_periods(json_file, tx, ty)
        param = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/civilTools")
        show_at_startup = self.form.show_at_startup.isChecked()
        param.SetBool("FirstTime", show_at_startup)
        ostan = self.get_current_ostan()
        city = self.get_current_city()
        param.SetString("ostan", ostan)
        param.SetString("city", city)

    def xactivate(self):
        if self.form.x_treeWidget.currentItem().parent():
            system = self.form.x_treeWidget.currentItem().parent().text(0)
            lateral = self.form.x_treeWidget.currentItem().text(0)
            self.form.y_treeWidget.scrollToItem(self.form.x_treeWidget.currentItem())
            return (system, lateral)
        return None

    def yactivate(self):
        if self.form.y_treeWidget.currentItem().parent():
            system = self.form.y_treeWidget.currentItem().parent().text(0)
            lateral = self.form.y_treeWidget.currentItem().text(0)
            return (system, lateral)
        return None

    def setA(self):
        sotoh = ['خیلی زیاد', 'زیاد', 'متوسط', 'کم']
        ostan = self.get_current_ostan()
        city = self.get_current_city()
        try:
            A = int(ostanha.ostans[ostan][city][0])
            self.form.accText.setText(sotoh[A - 1])
        except KeyError:
            pass
