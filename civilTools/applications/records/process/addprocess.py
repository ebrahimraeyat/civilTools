from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from .process import Process as process

process_win, base_win = uic.loadUiType('applications/records/widgets/process.ui')


class ProcessWin(base_win, process_win):
    def __init__(self, original_earthquakes, parent=None):
        super(ProcessWin, self).__init__()
        self.setupUi(self)
        self.creat_connections()
        # try:
        #     self.load_settings()
        # except:
        #     pass
        self.original_earthquakes = original_earthquakes.copy()
        self.process_original_list.addItems(original_earthquakes.keys())
        self.selected_earthquakes = {}
        self.process = {'X':{}, 'Y':{}, 'Z':{}}

    # def load_settings(self):
    #     settings = QSettings()
    #     self.restoreGeometry(settings.value("AddEarthquake\Geometry"))
    #     self.splitter.restoreState(settings.value("AddEarthquake\Splitter"))

    # def closeEvent(self, event):
    #     settings = QSettings()
    #     settings.setValue("AddEarthquake\Geometry",
    #                       QVariant(self.saveGeometry()))
    #     settings.setValue("AddEarthquake\Splitter",
    #             QVariant(self.splitter.saveState()))

    def accept(self):
        if not self.process_selected_list.count():
            return
        for key, value in self.selected_earthquakes.items():
            for direction in self.process.keys():
                self.process[direction][key] = value.accelerations[direction.lower()]
        QDialog.accept(self)
        
    def creat_connections(self):
    	self.add_process_button.clicked.connect(self.add_process)
    	self.remove_process_button.clicked.connect(self.remove_process)

    def add_process(self):
        selected_items = self.process_original_list.selectedItems()
        for item in selected_items:
            earthquake_name = item.text()
            earthquake = self.original_earthquakes.pop(earthquake_name)
            self.process_original_list.takeItem(self.process_original_list.row(item))
            self.selected_earthquakes[earthquake_name] = earthquake
            self.process_selected_list.addItem(item)

    def remove_process(self):
        selected_items = self.process_selected_list.selectedItems()
        for item in selected_items:
            earthquake_name = item.text()
            earthquake = self.selected_earthquakes.pop(earthquake_name)
            self.process_selected_list.takeItem(self.process_selected_list.row(item))
            self.original_earthquakes[earthquake_name] = earthquake
            self.process_original_list.addItem(item)
