
__title__ = "Discretize"
__author__ = "Christophe Grellier (Chris_G)"
__license__ = "LGPL 2.1"
__doc__ = "Discretize an edge or a wire."
__usage__ = """Select an edge in the 3D View
Activate tool
It will generate some points along the edge, following various methods"""

from pathlib import Path

from PySide2 import QtCore
from PySide2.QtWidgets import QMessageBox

import FreeCAD
import FreeCADGui
import Part



class CivilToolsDiscretize:
    def parseSel(self, selectionObject):
        res = []
        for obj in selectionObject:
            if obj.HasSubObjects:
                subobj = obj.SubObjects[0]
                if issubclass(type(subobj), Part.Edge):
                    res.append((obj.Object, [obj.SubElementNames[0]]))
            elif hasattr(obj.Object, "Shape") and hasattr(obj.Object.Shape, "Edge1"):
                res.append((obj.Object, ["Edge1"]))
        return res

    def Activated(self):
        s = FreeCADGui.Selection.getSelectionEx()
        edges = self.parseSel(s)
        if not edges:
            FreeCAD.Console.PrintError("{} :\n{}\n".format(__title__, __usage__))
        FreeCADGui.doCommand("from py_widget.tools import discretize")
        for e in edges:
            FreeCADGui.doCommand('obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Discretized_Edge")')
            FreeCADGui.doCommand('discretize.Discretization(obj, (FreeCAD.ActiveDocument.getObject("{}"),"{}"))'.format(e[0].Name, e[1][0]))
            FreeCADGui.doCommand('discretize.ViewProviderDisc(obj.ViewObject)')
            FreeCADGui.doCommand('obj.ViewObject.PointSize = 3')
            # obj=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Discretized_Edge")
            # Discretization(obj,e)
            # ViewProviderDisc(obj.ViewObject)
            # obj.ViewObject.PointSize = 3.00000
        FreeCAD.ActiveDocument.recompute()

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            __title__)
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "{}<br><br><b>Usage :</b><br>{}".format(__doc__, "<br>".join(__usage__.splitlines())))
        path = str(
                   Path(__file__).parent.absolute().parent.parent / "images" / "discretize.svg"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}


        