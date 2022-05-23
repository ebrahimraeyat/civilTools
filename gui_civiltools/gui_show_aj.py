
from pathlib import Path

from PySide2 import QtCore


class CivilShowAj:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civil_show_aj",
            "Show Aj")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civil_show_aj",
            "Show Static and Dynamic Aj Tables and Apply Aj to ETABS Model")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "show_aj.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        from gui_civiltools.gui_check_legal import (
            allowed_to_continue,
            show_warning_about_number_of_use
        )
        allow, check = allowed_to_continue(
            'export_to_etabs.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/7f10571fab2a08b7a17ab782778e53e1/raw',
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
        from py_widget import aj_correction
        win = aj_correction.Form(etabs)
        import FreeCADGui as Gui
        Gui.Control.showDialog(win)
        # mdi = get_mdiarea()
        # if not mdi:
        #     return None
        # sub = mdi.addSubWindow(win)
        # sub.show()
        show_warning_about_number_of_use(check)
        
    def IsActive(self):
        return True

def get_mdiarea():
    """ Return FreeCAD MdiArea. """
    import FreeCADGui as Gui
    import PySide2
    mw = Gui.getMainWindow()
    if not mw:
        return None
    childs = mw.children()
    for c in childs:
        if isinstance(c, PySide2.QtWidgets.QMdiArea):
            return c
    return None


        