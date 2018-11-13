import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic
# import pandas as pd
import pickle
import numpy as np
#from pandas.tools.plotting import table
##matplotlib.use("Agg")
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# import matplotlib.pyplot as plt
from .earthquake import addearthquake, earthquake
from .process import addprocess, process
import pyqtgraph as pg
## Switch to using white background and black foreground
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
main_window = uic.loadUiType('applications/records/widgets/mainwindow.ui')[0]


class Record(QMainWindow, main_window):

    def __init__(self, parent=None):
        super(Record, self).__init__(parent)
        self.setupUi(self)
        self.dirty = False
        self.lastDirectory = ''
        self.filename = None
        self.create_connections()
        try:
            self.load_settings()
        except:
            pass
        self.earthquakes = {}
        self.min_earthquakes_dt = 1.0
        self.max_eff_duration = 1.0
        self.__set_labels()

    def create_connections(self):
        self.add_earth_button.clicked.connect(self.add_earthquake)
        self.x_radioButton.clicked.connect(self.__plot_accelerated)
        self.y_radioButton.clicked.connect(self.__plot_accelerated)
        self.z_radioButton.clicked.connect(self.__plot_accelerated)
        self.x_radioButton.clicked.connect(self._display_earthquake_prop)
        self.y_radioButton.clicked.connect(self._display_earthquake_prop)
        self.z_radioButton.clicked.connect(self._display_earthquake_prop)
        self.save_earthquakes_button.clicked.connect(self.save_earthquakes)
        self.load_earthquakes_button.clicked.connect(self.load_earthquakes)
        self.earthquake_list.currentItemChanged.connect(self.__plot_accelerated)
        self.earthquake_list.currentItemChanged.connect(self._display_earthquake_prop)
        self.clear_earths_button.clicked.connect(self.clear_earthquakes)
        self.interpolate_earths_button.clicked.connect(self.interpolate_earthquakes)
        self.scale_earths_button.clicked.connect(self.scale_earthquakes)
        self.unify_earth_durations_button.clicked.connect(self.unify_duration_of_earthquakes)
        self.action_Report.triggered.connect(self.create_report)
        self.s0_SpinBox.valueChanged.connect(self.draw_canai_tajimi)
        self.w0_SpinBox.valueChanged.connect(self.draw_canai_tajimi)
        self.xi0_SpinBox.valueChanged.connect(self.draw_canai_tajimi)
        self.start_process_button.clicked.connect(self.start_process)
        self.process_dir_list.currentItemChanged.connect(self.__plot_process)
        self.s0_process_SpinBox.valueChanged.connect(self.draw_process_canai_tajimi)
        self.w0_process_SpinBox.valueChanged.connect(self.draw_process_canai_tajimi)
        self.xi0_process_SpinBox.valueChanged.connect(self.draw_process_canai_tajimi)

    def load_settings(self):
        settings = QSettings()
        self.restoreGeometry(settings.value("Record\Geometry"))
        self.restoreState(settings.value("Record\State"))
        self.splitter.restoreState(settings.value("Record\Splitter"))
        self.splitter_2.restoreState(settings.value("Record\Splitter2"))

    def closeEvent(self, event):
        if  (self.dirty and
            QMessageBox.question(self, "earthquakes - Save?",
                    "Save unsaved changes?",
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel) ==
                    QMessageBox.Yes):
            self.save_earthquakes()
        settings = QSettings()
        settings.setValue("Record\Geometry",
                          QVariant(self.saveGeometry()))
        settings.setValue("Record\State",
                          QVariant(self.saveState()))
        settings.setValue("Record\Splitter",
                QVariant(self.splitter.saveState()))
        settings.setValue("Record\Splitter2",
                QVariant(self.splitter_2.saveState()))
        event.accept()
    def save_earthquakes(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'save earthquakes',
                                               self.lastDirectory)
        if not filename:
            return
        l = {'min_dt':self.min_earthquakes_dt,
             'max_eff_duration': self.max_eff_duration,
             'earthquakes': self.earthquakes}
        pickle.dump(l, open(filename, "wb"))
        self.dirty = False

    def load_earthquakes(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'open earthquakes',
                                               self.lastDirectory)
        if not filename:
            return
        l = pickle.load(open(filename, "rb"))
        self.min_earthquakes_dt = l['min_dt']
        self.max_eff_duration = l['max_eff_duration']
        self.earthquakes = l['earthquakes']
        self.earthquake_list.clear()
        self.earthquake_list.addItems(self.earthquakes.keys())
        # for earthquake in self.earthquakes.values():
        #     for acc in earthquake.accelerations.values():
        #         acc.reset_prop()
        if self.earthquake_list.count() > 0:
            self.earthquake_list.setCurrentRow(0)
                
        self.min_dt_label.setText(f"min = {self.min_earthquakes_dt}")

    def add_earthquake(self):
        win = addearthquake.AddEarthquakeWin(self)
        if win.exec_():
            new_earthquake = earthquake.Earthquake(win.accelerated['x'], win.accelerated['y'], win.accelerated['z'])
            if new_earthquake.dt < self.min_earthquakes_dt:
                self.min_earthquakes_dt = new_earthquake.dt
            if new_earthquake.eff_duration > self.max_eff_duration:
                self.max_eff_duration = new_earthquake.eff_duration
            name = '{}_{}'.format(new_earthquake.name, new_earthquake.station)
            self.earthquakes[name] = new_earthquake
            self.earthquake_list.addItem(name)
            if self.earthquake_list.count() == 1:
                self.earthquake_list.setCurrentRow(0)
            self.min_dt_label.setText(f"min = {self.min_earthquakes_dt}")
        self.dirty = True

    def __plot_accelerated(self):
        if not self.earthquake_list.count():
            return
        if self.earthquake_list.currentRow() == -1:
            return
        self.__clear_accelerated_plot()
        direction = self.__direction()
        earthquake_name = self.earthquake_list.currentItem().text()
        earthquake = self.earthquakes[earthquake_name]
        accelerated = earthquake.accelerations[direction]
        self.accelerated_time_history.plot(accelerated.time, accelerated.acc)
        self.accelerated_density_func.plot(accelerated.x[:-1], accelerated.density_func.values)
        self.accelerated_distributed_func.plot(accelerated.x[:-1], accelerated.distribute_func.values)
        self.accelerated_r_tow.plot(accelerated.tow, accelerated.r_tow)
        self.accelerated_s_w.plot(accelerated.ws, accelerated.s_w)
        self.fourier_amplitude.plot(accelerated.freq, accelerated.fourier_amplitude)
        # print(dir(self.accelerated_time_history))
        # self.accelerated_s_w.plot(accelerated.ws_canai, accelerated.s_w_canai)

    def __set_labels(self):
        self.accelerated_time_history.setLabel('bottom', text='Time [sec]')
        self.accelerated_time_history.setLabel('left', text="Acc [g]")
        self.accelerated_density_func.setLabel('bottom', text='Acc [g]')
        self.accelerated_density_func.setLabel('left', text='%')
        self.accelerated_density_func.setTitle('Probability Density Function (PDF)')
        self.accelerated_distributed_func.setLabel('bottom', text='Acc [g]')
        self.accelerated_distributed_func.setLabel('left', text="%")
        self.accelerated_distributed_func.setTitle('Cumulative Distribution Function (CDF)')
        self.accelerated_r_tow.setLabel('bottom', text='<font>&tau;</font> [Sec]')
        self.accelerated_r_tow.setLabel('left', text='[g] ^ 2')
        self.accelerated_r_tow.setTitle('Auto Correlation Function')
        self.accelerated_s_w.setLabel('bottom', text='<font>&omega;</font> [Hz]')
        self.accelerated_s_w.setLabel('left', text='[g] ^ 2 - rad - Sec')
        self.accelerated_s_w.setTitle('Density Function')
        self.fourier_amplitude.setLabel('bottom', text='<font>&omega;</font> [Hz]')
        self.fourier_amplitude.setLabel('left', text="Fourier Amplitude")
        self.fourier_amplitude.setTitle('Frequency content')
        # process labels
        # self.process_expexted_pow1.setLabel('bottom', text='Time [sec]')
        self.process_expexted_pow1.setLabel('left', text="Acc [g]")
        self.process_expexted_pow1.setTitle('E[X]')
        # self.process_expexted_pow2.setLabel('bottom', text='Time [sec]')
        self.process_expexted_pow2.setLabel('left', text="Acc [g]")
        self.process_expexted_pow2.setTitle('E[X<sup>2</sup>]')
        self.process_expexted_pow3.setLabel('bottom', text='Time [sec]')
        self.process_expexted_pow3.setLabel('left', text="Acc [g]")
        self.process_expexted_pow3.setTitle('E[X<sup>3</sup>]')
        self.process_r_tow.setLabel('bottom', text='<font>&tau;</font> [Sec]')
        self.process_r_tow.setLabel('left', text='[g] ^ 2')
        self.process_r_tow.setTitle('Auto Correlation Function')
        self.process_s_w.setLabel('bottom', text='<font>&omega;</font> [Hz]')
        self.process_s_w.setLabel('left', text='[g] ^ 2 - rad - Sec')
        self.process_s_w.setTitle('Density Function')

    def interpolate_earthquakes(self):
        dt = self.dt_SpinBox.value()
        if dt == 0:
            dt = self.min_earthquakes_dt
        if (self.earthquake_list.count() and
            QMessageBox.question(self, "interpolate - earthquakes?",
                f"interpolate all earthquakes with dt = {dt}?",
                QMessageBox.Yes | QMessageBox.No) ==
                QMessageBox.Yes):
            for i, earthquake in enumerate(self.earthquakes.values()):
                earthquake.interpolate_earthquake(dt)
                self.update_progressBar(i)
            self.__plot_accelerated()
            self.dt_SpinBox.setValue(dt)
            QMessageBox.information(self, "Successful !", 
                f"All earthquakes Interpolated to dt = {dt}")
            self.update_progressBar(-1)
        self.min_dt_label.setText(f"min = {self.min_earthquakes_dt}")
        self.dirty = True

    def scale_earthquakes(self):
        sf = self.scale_SpinBox.value()
        if sf == 0:
            sf = 1
        if (self.earthquake_list.count() and
            QMessageBox.question(self, "scale - earthquakes?", 
                f"scale all earthquakes to {sf} g?",
                QMessageBox.Yes | QMessageBox.No) ==
                QMessageBox.Yes):
            for i, earthquake in enumerate(self.earthquakes.values()):
                earthquake.scale(sf)
                self.update_progressBar(i)   
            self.__plot_accelerated()
            QMessageBox.information(self, "Successful !", 
                f"All earthquakes Scaled to Acceleration = {sf} g")
            self.update_progressBar(-1)
        self.dirty = True

    def unify_duration_of_earthquakes(self):
        duration = self.unify_duration_SpinBox.value()
        if duration == 0:
            duration = self.max_eff_duration
        if (self.earthquake_list.count() and
            QMessageBox.question(self, "unify duration - earthquakes?", 
                f"unify duration of all earthquakes to {duration} sec?",
                QMessageBox.Yes | QMessageBox.No) ==
                QMessageBox.Yes):
            for i, earthquake in enumerate(self.earthquakes.values()):
                earthquake.cut(duration)
                print(earthquake.name, earthquake.number_of_points)
                self.update_progressBar(i)
            self.__plot_accelerated()
            QMessageBox.information(self, "Successful !", 
                f"All earthquakes unified to duration = {duration} Sec")
            self.update_progressBar(-1)
        self.dirty = True

    def update_progressBar(self, i):
        self.progressBar.setValue(100 * (i + 1) / len(self.earthquakes))

    def __clear_accelerated_plot(self):
        self.accelerated_time_history.clear()
        self.accelerated_density_func.clear()
        self.accelerated_distributed_func.clear()
        self.accelerated_r_tow.clear()
        self.accelerated_s_w.clear()
        self.fourier_amplitude.clear()

    def draw_canai_tajimi(self):
        if not self.earthquake_list.count():
            return
        if self.earthquake_list.currentRow() == -1:
            return
        s0 = self.s0_SpinBox.value()
        w0 = self.w0_SpinBox.value()
        xi0 = self.xi0_SpinBox.value()
        direction = self.__direction()
        earthquake_name = self.earthquake_list.currentItem().text()
        earthquake = self.earthquakes[earthquake_name]
        accelerated = earthquake.accelerations[direction]
        ws_canai, s_w_canai = accelerated.canai_tajimis(s0, w0, xi0)
        pen = pg.mkPen('b', width=1)
        try:
            self.accelerated_s_w.removeItem(self.canai_item)
        except:
            pass
        self.canai_item = pg.PlotDataItem(ws_canai, s_w_canai, connect="finite", pen=pen)
        self.accelerated_s_w.addItem(self.canai_item)

    def clear_earthquakes(self):
        if (self.earthquake_list.count() and
            QMessageBox.question(self, "clear - earthquakes?",
                "clear all earthquakes?",
                QMessageBox.Yes | QMessageBox.No) ==
                QMessageBox.Yes):
            self.__clear_accelerated_plot()
            self.earthquake_list.clear()
            self.earthquakes = {}

    def _display_earthquake_prop(self):
        if self.earthquake_list.currentItem() is None:
            return
        earthquake_name = self.earthquake_list.currentItem().text()
        earthquake = self.earthquakes[earthquake_name]
        direction = self.__direction()
        accelerated = earthquake.accelerations[direction]
        s = earthquake.__str__() + accelerated.__str__()
        self.earth_prop_textEdit.setText(s)

    def create_report(self):
        pass
        # exporter = pg.exporters.ImageExporter(self.accelerated_time_history.plotItem)
        # # save to file
        # exporter.export('fileName.png')
        
    def __direction(self):
        '''
        return direction that selected in earthquake direction groupbox
        '''
        if self.x_radioButton.isChecked():
            return 'x'
        if self.y_radioButton.isChecked():
            return 'y'
        return 'z'

            # ax = self.figure.add_subplot(311)
            # plotWidget = Work_on_record_file(self.filename, .005)
            # plotWidget.acc.plot(title='Acceleration', ax=ax, legend=None)
            # ax = self.figure.add_subplot(312)
            # plotWidget.density_function.plot(title='density function', ax=ax, kind='bar', legend=None)
            # ax = self.figure.add_subplot(313)
            # #table(ax, sr_info, loc='center right', fontsize=30, colWidths=[0.1])
            # plotWidget.distribute_function.plot(title='distribute function', ax=ax, legend=None)
            # self.canvas.draw()

            # sr_info = pd.Series(plotWidget.return_dict)
            # html = ''
            # for key, value in sr_info.iteritems():
            #     html += '<p>{}: {}</p>\n'.format(key, value)
            # self.info_text_browser.setHtml(html)

    def start_process(self):
        win = addprocess.ProcessWin(self.earthquakes, self)
        if win.exec_():
            self.process = {}
            for direction, e in win.process.items():
                pro = process.Process(e)
                pro.set_properties()
                pro.reset_prop()
                self.process[direction] = pro
            self.process_list.clear()
            self.process_list.addItems([*pro.accelerations.keys()])
            self.__plot_process()

    def __plot_process(self):
        if self.process_dir_list.currentItem() is None:
            return
        self.__clear_process_plot()
        direction = self.process_dir_list.currentItem().text()
        pro = self.process[direction]
        self.process_r_tow.plot(pro.tow, pro.r_tow)
        self.process_s_w.plot(pro.ws, pro.s_w)
        self.process_expexted_pow1.plot(pro.time, pro.ex)
        self.process_expexted_pow2.plot(pro.time, pro.ex2)
        self.process_expexted_pow3.plot(pro.time, pro.ex3)
        # self.process_density_func.plot(pro.x[:-1], pro.density_func)
        # print(self.process)

    def __clear_process_plot(self):
        self.process_r_tow.clear()
        self.process_s_w.clear()
        self.process_expexted_pow1.clear()
        self.process_expexted_pow2.clear()
        self.process_expexted_pow3.clear()
        # self.process_density_func.clear()

    def draw_process_canai_tajimi(self):
        if not self.process_list.count():
            return
        if self.process_dir_list.currentRow() == -1:
            return
        s0 = self.s0_process_SpinBox.value()
        w0 = self.w0_process_SpinBox.value()
        xi0 = self.xi0_process_SpinBox.value()
        process = self.process['X']
        ws_canai, s_w_canai = process.canai_tajimis(s0, w0, xi0)
        pen = pg.mkPen('b', width=1)
        try:
            self.process_s_w.removeItem(self.canai_process_item)
        except:
            pass
        self.canai_process_item = pg.PlotDataItem(ws_canai, s_w_canai, connect="finite", pen=pen)
        self.process_s_w.addItem(self.canai_process_item)
                

        
            # for e in selected_earthquakes:
            #     x_process = 
            # new_earthquake = earthquake.Earthquake(win.accelerated['x'], win.accelerated['y'], win.accelerated['z'])
            # if new_earthquake.dt < self.min_earthquakes_dt:
            #     self.min_earthquakes_dt = new_earthquake.dt
            # if new_earthquake.eff_duration > self.max_eff_duration:
            #     self.max_eff_duration = new_earthquake.eff_duration
            # name = '{}_{}'.format(new_earthquake.name, new_earthquake.station)
            # self.earthquakes[name] = new_earthquake
            # self.earthquake_list.addItem(name)
            # if self.earthquake_list.count() == 1:
            #     self.earthquake_list.setCurrentRow(0)
            # self.min_dt_label.setText(f"min = {self.min_earthquakes_dt}")
        self.dirty = True


    def getLastSaveDirectory(self, f):
        return os.sep.join(f.split(os.sep)[:-1])

    def getFilename(self, prefixes):
        filters = ''
        for prefix in prefixes:
            filters += "{}(*.{})".format(prefix, prefix)
        filename = QFileDialog.getSaveFileName(self, ' خروجی ',
                                               self.lastDirectory, filters)
        if filename == '':
            return
        self.lastDirectory = self.getLastSaveDirectory(filename)
        return filename

if __name__ == "__main__":

    app = QApplication(sys.argv)
    # pixmap = QPixmap("./images/run.png")
    # splash = QSplashScreen(pixmap)
    # splash.show()
    # app.processEvents()
    global defaultPointsize
    font = QFont()
    font.setFamily("Tahoma")
    if sys.platform.startswith('linux'):
        defaultPointsize = 10
        font.setPointSize(defaultPointsize)
    else:
        defaultPointsize = 9
        font.setPointSize(defaultPointsize)
    app.setFont(font)
    app.setOrganizationName("Ebrahim Raeyat")
    app.setOrganizationDomain("ebrahimraeyat.blog.ir")
    app.setApplicationName("section prop")
    #app.setWindowIcon(QIcon(":/icon.png"))
    window = Record()
    window.show()
    app.exec_()
