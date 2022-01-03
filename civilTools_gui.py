import os
from pathlib import Path
from PySide2 import QtCore
from PySide2.QtWidgets import QMessageBox
# import FreeCAD
import FreeCADGui as Gui
# import DraftTools
# import civiltoolswelcome


from gui_civiltools import (
    gui_earthquake_factor,
    gui_irregurality_of_mass,
    gui_explod_load_patterns,
    gui_story_stiffness,
    gui_get_weakness,
    gui_show_torsion,
    gui_create_period_file,
    # gui_automatic_drift,
    gui_modify_torsion_stiffness,
    gui_show_story_forces,
    gui_show_story_stiffness,
    gui_show_weakness,
    gui_show_aj,
    gui_scale_response_spec,
    gui_high_pressure_columns,
    gui_assign_frame_sections,
    gui_offset_beams,
    gui_wall_load_on_frames,
    )


def QT_TRANSLATE_NOOP(ctx, txt): return txt



class CivilHelp:

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            "Civil_help",
            "Help")
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            "Civil_help",
            "Help")
        path = str(
                   Path(__file__).parent.absolute() / "Resources" / "icons" / "help.svg"
                   )
        return {'Pixmap': path,
                'MenuText': MenuText,
                'ToolTip': ToolTip}
    def Activated(self):
        import webbrowser
        path = str(
                   Path(__file__).parent.absolute() / "help" / "help.pdf"
                   )
        webbrowser.open_new(path)

    def IsActive(self):
        return True


def get_save_filename(ext):
    from PySide2.QtWidgets import QFileDialog
    filters = f"{ext[1:]} (*{ext})"
    filename, _ = QFileDialog.getSaveFileName(None, 'select file',
                                              None, filters)
    if not filename:
        return
    if not ext in filename:
        filename += ext
    return filename

def allowed_to_continue(
                        filename,
                        gist_url,
                        dir_name,
                        n = 2,
                        ):
    from functions import check_legal
    check = check_legal.CheckLegalUse(
                                filename,
                                gist_url,
                                dir_name,
                                n = n,
    )
    allow, text = check.allowed_to_continue()
    if allow and not text:
        return True, check
    else:
        if text in ('INTERNET', 'SERIAL'):
            ui = SerialForm()
            ui.form.serial.setText(check.serial)
            Gui.Control.showDialog(ui)
            # if ui.setupUi():
            #     Gui.Control.closeDialog(ui)
            return False, check
        elif text == 'REGISTERED':
            msg = "Congrajulation! You are now registered, enjoy using this features!"
            QMessageBox.information(None, 'Registered', str(msg))
            return True, check
    return False, check

def show_warning_about_number_of_use(check):
    check.add_using_feature()
    _, no_of_use = check.get_registered_numbers()
    n = check.n - no_of_use
    if n > 0:
        msg = f"You can use this feature {n} more times!\n then you must register the software."
        QMessageBox.warning(None, 'Not registered!', str(msg))

class SerialForm:
    def __init__(self):
        serial_ui = str(
            Path(__file__).parent.absolute() / 'Resources' / 'ui' / 'serial.ui'
            )
        self.form = Gui.PySideUic.loadUi(serial_ui)




# Gui.addCommand('Civil_help', CivilHelp())
Gui.addCommand('civil_earthquake_factor', gui_earthquake_factor.CivilEarthquakeFactor())
Gui.addCommand('civil_irregurality_of_mass', gui_irregurality_of_mass.CivilIrregularityOfMass())
Gui.addCommand('civil_explod_load_patterns', gui_explod_load_patterns.CivilExplodLoadPatterns())
Gui.addCommand('civil_story_stiffness', gui_story_stiffness.CivilStoryStiffness())
Gui.addCommand('civil_get_weakness', gui_get_weakness.CivilGetWeakness())
Gui.addCommand('civil_show_torsion', gui_show_torsion.CivilShowTorsion())
Gui.addCommand('civil_create_period_file', gui_create_period_file.CivilCreatePeriodFile())
# Gui.addCommand('civil_automatic_drift', gui_automatic_drift.CivilAutomaticDrift())
Gui.addCommand('civil_modify_torsion_stiffness', gui_modify_torsion_stiffness.CivilBeamJ())
Gui.addCommand('civil_show_story_forces', gui_show_story_forces.CivilStoryForces())
Gui.addCommand('civil_show_story_stiffness', gui_show_story_stiffness.CivilShowStoryStiffness())
Gui.addCommand('civil_show_weakness', gui_show_weakness.CivilShowWeakness())
Gui.addCommand('civil_show_aj', gui_show_aj.CivilShowAj())
Gui.addCommand('civil_scale_response_spec', gui_scale_response_spec.CivilScaleResponseSpec())
Gui.addCommand('civil_high_pressure_columns', gui_high_pressure_columns.CivilHighPressureColumns())
Gui.addCommand('civil_assign_frame_sections', gui_assign_frame_sections.CivilAssignFrameSections())
Gui.addCommand('civil_offset_beams', gui_offset_beams.CivilOffsetBeam())
Gui.addCommand('civil_wall_load_on_frames', gui_wall_load_on_frames.CivilWallLoadOnFrames())

civiltools_list = [
            "civil_earthquake_factor",
            "civil_irregurality_of_mass",
            "civil_explod_load_patterns",
            "civil_story_stiffness",
            "civil_get_weakness",
            "civil_show_torsion",
            # "civil_automatic_drift",
            "civil_create_period_file",
            "civil_modify_torsion_stiffness",
            "civil_show_story_forces",
            "civil_show_story_stiffness",
            "civil_show_weakness",
            "civil_show_aj",
            "civil_scale_response_spec",
            "civil_high_pressure_columns",
            ]
civiltools_assign = [
            "civil_assign_frame_sections",
            "civil_wall_load_on_frames",
            ]

civiltools_tools = [
            "civil_offset_beams",
            ]
