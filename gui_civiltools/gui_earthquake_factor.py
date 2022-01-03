
from pathlib import Path

import PySide2
from PySide2 import QtCore

import FreeCAD
import FreeCADGui as Gui



class CivilEarthquakeFactor:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "Civil",
            "Earthquake Factors")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "Civil",
            "Calculate Earthquake Factors and Write to ETABS Model")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "earthquake.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        # def get_mdiarea():
        #     """ Return FreeCAD MdiArea. """
        #     mw = Gui.getMainWindow()
        #     if not mw:
        #         return None
        #     childs = mw.children()
        #     for c in childs:
        #         if isinstance(c, PySide2.QtWidgets.QMdiArea):
        #             return c
        #     return None

        # mdi = get_mdiarea()
        # if not mdi:
        #     return None
        # self.initiate()
        import etabs_obj
        etabs = etabs_obj.EtabsModel()
        if not etabs.success:
            from PySide2.QtWidgets import QMessageBox
            QMessageBox.warning(None, 'ETABS', 'Please open etabs file!')
            return False
        from py_widget import earthquake_factor
        win = earthquake_factor.Form(etabs)
        Gui.Control.showDialog(win)
        # sub = mdi.addSubWindow(win.form)
        # sub.show()
        
    def IsActive(self):
        return True

    def initiate(self):
        doc = FreeCAD.ActiveDocument
        if doc is None:
            doc = FreeCAD.newDocument()
        if not hasattr(doc, 'Site'):
            import Arch
            site = Arch.makeSite([])
            build = Arch.makeBuilding([])
            # build.recompute()
            site.Group = [build]
            doc.recompute()

        