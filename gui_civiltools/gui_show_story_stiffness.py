
from pathlib import Path

from PySide import QtCore

import FreeCADGui as Gui


class CivilShowStoryStiffness:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_show_story_stiffness",
            "Story stiffness")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civil_show_story_stiffness",
            "Show Stories Stiffness")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "show_stiffness.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        import find_etabs
        etabs, filename = find_etabs.find_etabs(run=False, backup=False)
        if (
            etabs is None or
            filename is None
            ):
            return
        from py_widget import show_siffness_story_way
        win = show_siffness_story_way.Form(etabs)
        e_name = etabs.get_file_name_without_suffix()
        way_radio_button = {'2800': win.form.radio_button_2800,
                            'modal': win.form.radio_button_modal,
                            'earthquake': win.form.radio_button_earthquake}
        for w, rb in way_radio_button.items():
            name = f'{e_name}_story_stiffness_{w}_table.json'
            json_file = Path(etabs.SapModel.GetModelFilepath()) / name
            if not json_file.exists():
                rb.setChecked(False)
                rb.setEnabled(False)
        Gui.Control.showDialog(win)
        
    def IsActive(self):
        return True


        