
from pathlib import Path

from PySide import QtCore
from PySide.QtGui import QMessageBox

import FreeCADGui as Gui



class CivilToolsCheckDeflectionOfBeams:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Beam Deflection")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Check Deflection for selected beams")
        path = str(
                   Path(__file__).parent.absolute().parent.parent / "images" / "deflection.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        from gui_civiltools.gui_check_legal import (
                allowed_to_continue,
                show_warning_about_number_of_use,
                )
        allow, check = allowed_to_continue(
            'check_deflection.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/74c1a371b99c62de47472a6046a91a97/raw',
            'cfactor'
            )
        if not allow:
            return
        import find_etabs
        etabs, filename = find_etabs.find_etabs(run=False, backup=False)
        if (
            etabs is None or
            filename is None
            ):
            return
        # Get selected beams
        selected = etabs.select_obj.get_selected_objects()
        frame_names = selected.get(2, [])
        beam_names = []
        for name in frame_names:
            if (etabs.frame_obj.is_beam(name) and
                etabs.SapModel.FrameObj.GetDesignProcedure(name)[0] == 2
            ):
                beam_names.append(name)
        if len(beam_names) == 0:
            QMessageBox.warning(None, 'Select Beams', 'Select Beams in ETABS Model.')
            return
        from exporter import civiltools_config
        d = civiltools_config.get_settings_from_etabs(etabs)
        if len(d) == 0:
            QMessageBox.warning(None, 'Settings', 'Please Set Options First!')
            Gui.runCommand("civiltools_settings")
            d = civiltools_config.get_settings_from_etabs(etabs)
        if len(d) == 0:
            return
        from py_widget.control import control_deflection_of_beams
        win = control_deflection_of_beams.Form(etabs, beam_names=beam_names, d=d)
        find_etabs.show_win(win, in_mdi=False)
        show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True


Gui.addCommand("civilTools_check_deflection_of_beams", CivilToolsCheckDeflectionOfBeams())