from pathlib import Path
from PySide2 import  QtWidgets, QtCore
import FreeCADGui as Gui

import civiltools_rc
UPDATEINTERVAL = 500 # number of milliseconds between  update

civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_model, obj_):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'tools' / 'match_property.ui'))
        self.etabs = etabs_model
        self.SapModel = self.etabs.SapModel
        self.main_section = self.etabs.frame_obj.get_section_name(obj_)
        self.main_frame_type = self.SapModel.FrameObj.GetDesignOrientation(obj_)[0]
        self.frame_sections = {}
        self.update()
        self.create_connections()

    def get_selected(self):
        ret = self.SapModel.SelectObj.GetSelected()
        if ret[1][0] == 2:
            self.SapModel.SelectObj.ClearSelection()
            return ret[2][0]

        
    def create_connections(self):
        self.form.done_pushbutton.clicked.connect(self.reject)
        self.form.cancel_pushbutton.clicked.connect(self.reject)

    def update(self):
        refresh = False
        ret = (0, [], [])
        try:
            ret = self.SapModel.SelectObj.GetSelected()
        except IndexError:
            if len(self.frame_sections) > 1:
                print('Index Error')
                print(self.frame_sections)
                self.reject()
                return
        for type_, name in zip(ret[1], ret[2]):
            if (
                type_ == 2 and
                self.main_frame_type == self.SapModel.FrameObj.GetDesignOrientation(name)[0]
                ):
                section = self.frame_sections.get(name, None)
                if section is None:
                    refresh = True
                    section = self.etabs.frame_obj.get_section_name(name)
                    self.frame_sections[name] = section
                    self.etabs.frame_obj.set_section_name(name, self.main_section)
        deselected_frames = []
        for name, section in self.frame_sections.items():
            if name not in ret[2]:
                self.etabs.frame_obj.set_section_name(name, section)
                deselected_frames.append(name)
                refresh = True
        for name in deselected_frames:
            del self.frame_sections[name]
        if refresh:
            self.SapModel.View.RefreshView()
        QtCore.QTimer.singleShot(UPDATEINTERVAL, self.update)


    def reject(self):
        Gui.Control.closeDialog()

    def getStandardButtons(self):
        return 0



