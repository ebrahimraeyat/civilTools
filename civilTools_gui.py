import os
from pathlib import Path
from PySide2 import QtCore
from PySide2.QtWidgets import QMessageBox
# import FreeCAD
import FreeCADGui as Gui
# import DraftTools
# import civiltoolswelcome


from gui_civiltools import (
    gui_civiltools_settings,
    gui_earthquake_factor,
    gui_irregurality_of_mass,
    gui_explod_load_patterns,
    gui_story_stiffness,
    gui_get_weakness,
    gui_show_torsion,
    gui_create_period_file,
    gui_automatic_drift,
    gui_modify_torsion_stiffness,
    gui_show_story_forces,
    gui_show_story_stiffness,
    gui_show_weakness,
    gui_show_aj,
    gui_scale_response_spec,
    gui_high_pressure_columns,
    gui_offset_beams,
    gui_wall_load_on_frames,
    gui_connect_beam,
    gui_distance_between_two_points,
    gui_create_section_cuts,
    gui_delete_backups,
    gui_restore_backups,
    gui_help,
    gui_check_legal,
    gui_100_30_columns,
    gui_import_model,
    )

from gui_civiltools.assign import (
    gui_assign_ev,
    gui_assign_modifiers,
)
from gui_civiltools.define import (
    gui_create_load_combinations,
    gui_frame_sections,
    gui_define_axes,
    gui_create_spectral,
)
from gui_civiltools.control import (
    gui_get_weakness_torsion,
    gui_control_joint_shear,
    gui_check_deflection,
    gui_check_deflection_of_beams,
    gui_check_deflection_of_slab,
)
from gui_civiltools.tools import (
    gui_discretize, 
    gui_match_property,
    gui_expand_area_load_sets,
    gui_run_design,
)

from gui_civiltools.import_export import (
    gui_dxf,
)

from freecad_py import civiltools_views


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
Gui.addCommand('civiltools_settings', gui_civiltools_settings.CivilToolsSettings())
Gui.addCommand('civil_earthquake_factor', gui_earthquake_factor.CivilEarthquakeFactor())
Gui.addCommand('civil_irregurality_of_mass', gui_irregurality_of_mass.CivilIrregularityOfMass())
Gui.addCommand('civil_explod_load_patterns', gui_explod_load_patterns.CivilExplodLoadPatterns())
Gui.addCommand('civil_story_stiffness', gui_story_stiffness.CivilStoryStiffness())
Gui.addCommand('civil_get_weakness', gui_get_weakness.CivilGetWeakness())
Gui.addCommand('civil_get_weakness_torsion', gui_get_weakness_torsion.CivilGetWeaknessTorsion())
Gui.addCommand('civil_show_torsion', gui_show_torsion.CivilShowTorsion())
Gui.addCommand('civil_create_period_file', gui_create_period_file.CivilCreatePeriodFile())
Gui.addCommand('civil_automatic_drift', gui_automatic_drift.CivilAutomaticDrift())
Gui.addCommand('civil_modify_torsion_stiffness', gui_modify_torsion_stiffness.CivilBeamJ())
Gui.addCommand('civil_show_story_forces', gui_show_story_forces.CivilStoryForces())
Gui.addCommand('civil_show_story_stiffness', gui_show_story_stiffness.CivilShowStoryStiffness())
Gui.addCommand('civil_show_weakness', gui_show_weakness.CivilShowWeakness())
Gui.addCommand('civil_show_aj', gui_show_aj.CivilShowAj())
Gui.addCommand('civil_scale_response_spec', gui_scale_response_spec.CivilScaleResponseSpec())
Gui.addCommand('civil_high_pressure_columns', gui_high_pressure_columns.CivilHighPressureColumns())
Gui.addCommand('civil_offset_beams', gui_offset_beams.CivilOffsetBeam())
Gui.addCommand('civil_connect_beam', gui_connect_beam.CivilConnectBeam())
Gui.addCommand('civil_distance_between_two_points', gui_distance_between_two_points.CivilDistance())
Gui.addCommand('civil_create_section_cuts', gui_create_section_cuts.CivilSectionCuts())
Gui.addCommand('civil_delete_backups', gui_delete_backups.CivilDeleteBackups())
Gui.addCommand('civil_restore_backups', gui_restore_backups.CivilRestoreBackups())
Gui.addCommand('civil_help', gui_help.CivilToolsHelp())
Gui.addCommand('civil_registe', gui_check_legal.CivilToolsRegister())
Gui.addCommand('civiltools_100_30', gui_100_30_columns.CivilTools100_30Columns())
Gui.addCommand('civiltools_import_model', gui_import_model.CivilToolsImportModel())
Gui.addCommand('civiltools_views',civiltools_views.CivilToolsViews())
Gui.addCommand('civiltools_discretize',gui_discretize.CivilToolsDiscretize())
Gui.addCommand('civiltools_create_spectral',gui_create_spectral.CivilToolsCreateSpectral())

civiltools_list = [
            "civil_automatic_drift",
            "civil_show_torsion",
            "civil_modify_torsion_stiffness",
            "civilTools_check_deflection_of_beams",
            "civilTools_check_deflection_of_slab",
            "civil_irregurality_of_mass",
            "civil_story_stiffness",
            "civil_get_weakness",
            "civil_get_weakness_torsion",
            "civil_create_period_file",
            "civil_show_story_forces",
            "civil_show_story_stiffness",
            "civil_show_weakness",
            "civil_show_aj",
            "civil_scale_response_spec",
            "civilTools_control_joint_shear",
            "civil_high_pressure_columns",
            "civiltools_100_30",
            "civil_earthquake_factor",
            "civiltools_create_spectral",
            ]
civiltools_assign = [
            "civiltools_wall_load",
            "civilTools_assign_modifiers",
            "civilTools_assign_ev",
            ]

civiltools_tools = [
            "Separator",
            "civiltools_run_and_design",
            "civilTools_match_property",
            "expand_area_load_sets",
            "civil_explod_load_patterns",
            "civil_offset_beams",
            "civil_connect_beam",
            "civil_distance_between_two_points",
            "civil_restore_backups",
            "civil_delete_backups",
            "civiltools_settings",
            "civiltools_discretize",
            "Draft_Move",
            "Draft_SelectPlane",
            ]

civiltools_view = [
            "civiltools_views",
            ]

civiltools_define = [
            "civilTools_define_axis",
            "civiltools_load_combinations",
            "civiltools_frame_sections",
            "civil_create_section_cuts",
            ]

civiltools_help = [
            "Separator",
            "civil_registe",
            "civil_help",
            ]

civiltools_import_export = [
    "civiltools_import_model",
    "civiltools_import_dxf",
]