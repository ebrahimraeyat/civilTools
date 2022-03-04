# -*- coding: utf-8 -*-

__title__ = "Discretize"
__author__ = "Christophe Grellier (Chris_G)"
__license__ = "LGPL 2.1"
__doc__ = "Discretize an edge or a wire."
__usage__ = """Select an edge in the 3D View
Activate tool
It will generate some points along the edge, following various methods"""

from pathlib import Path
import FreeCAD
import FreeCADGui
import Part
from .nurbs_tools import KnotVector


class Discretization:
    def __init__(self, obj, edge):
        obj.addProperty("App::PropertyLinkSub",      "Edge",      "Discretization",   "Edge").Edge = edge
        obj.addProperty("App::PropertyEnumeration",  "Target",    "Discretization",   "Tool target").Target=["Edge","Wire"]
        obj.addProperty("App::PropertyEnumeration",  "Algorithm", "Method",   "Discretization Method").Algorithm=["Number","QuasiNumber","Distance","Deflection","QuasiDeflection","Angular-Curvature"]
        obj.addProperty("App::PropertyInteger",      "Number",    "Method",   "Number of edge points").Number = 100
        obj.addProperty("App::PropertyFloat",        "Distance",  "Method",   "Distance between edge points").Distance=1.0
        obj.addProperty("App::PropertyFloat",        "Deflection","Method",   "Distance for deflection Algorithm").Deflection=1.0
        obj.addProperty("App::PropertyFloat",        "Angular",   "Method",   "Angular value for Angular-Curvature Algorithm").Angular=0.1
        obj.addProperty("App::PropertyFloat",        "Curvature", "Method",   "Curvature value for Angular-Curvature Algorithm").Curvature=0.1
        obj.addProperty("App::PropertyInteger",      "Minimum",   "Method",   "Minimum Number of points").Minimum = 2
        obj.addProperty("App::PropertyFloat",        "ParameterFirst",     "Parameters",   "Start parameter")
        obj.addProperty("App::PropertyFloat",        "ParameterLast",      "Parameters",   "End parameter")
        obj.addProperty("App::PropertyVectorList",   "Points",    "Discretization",   "Points")
        obj.addProperty("App::PropertyFloatList",
                        "NormalizedParameters",
                        "Output",
                        "Normalized parameters list")
        obj.setEditorMode("NormalizedParameters", 1)
        obj.Proxy = self
        obj.Algorithm = "Number"
        obj.Target = "Edge"
        edge = self.getTarget(obj, False)
        obj.ParameterFirst = edge.FirstParameter
        obj.ParameterLast = edge.LastParameter
        self.execute(obj)

    def edgeBounds(self, obj):
        o = obj.Edge[0]
        e = obj.Edge[1][0]
        n = eval(e.lstrip('Edge'))
        try:
            edge = o.Shape.Edges[n - 1]
            return edge.FirstParameter, edge.LastParameter
        except Exception:
            return 0.0, 1.0

    def getTarget(self, fp, typ):
        obj = fp.Edge[0]
        ssname = fp.Edge[1][0]
        sh = obj.Shape.copy()
        if hasattr(obj, "getGlobalPlacement"):
            gpl = obj.getGlobalPlacement()
            sh.Placement = gpl
        try:
            edge = sh.getElement(ssname)
            fp.setEditorMode("Target", 2)
            for w in sh.Wires:
                for e in w.Edges:
                    if edge.isSame(e):
                        fp.setEditorMode("Target", 0)
                        if typ:
                            return w
            return edge
        except Exception:
            return None

    def buildPoints(self, obj):
        target = self.getTarget(obj, obj.Target == "Wire")
        if not target:
            return False

        nb = obj.Number
        if target.isClosed():
            nb += 1

        kwargs = dict()
        if obj.Algorithm in ("Number", "QuasiNumber"):
            kwargs[obj.Algorithm] = nb
        elif obj.Algorithm in ("Deflection", "QuasiDeflection"):
            kwargs[obj.Algorithm] = obj.Deflection
        elif obj.Algorithm == "Distance":
            kwargs[obj.Algorithm] = obj.Distance
        elif obj.Algorithm == "Angular-Curvature":
            kwargs["Angular"] = obj.Angular
            kwargs["Curvature"] = obj.Curvature
            kwargs["Minimum"] = obj.Minimum

        fp = -1e-100
        lp = 1e100
        if obj.Target == "Edge":
            fp = obj.ParameterFirst
            lp = obj.ParameterLast
            if (fp >= target.FirstParameter) and (lp <= target.LastParameter) and (fp < lp):
                kwargs["First"] = fp
                kwargs["Last"] = lp

        pts = target.discretize(**kwargs)

        if pts[0].distanceToPoint(pts[-1]) < 1e-7:
            obj.Points = pts[:-1]
        else:
            obj.Points = pts
        return True

    def execute(self, obj):
        if not self.buildPoints(obj):
            return
        obj.Shape = Part.Compound([Part.Vertex(i) for i in obj.Points])
        if obj.Target == "Wire":
            w = self.getTarget(obj, True)
            target = w.approximate(1e-7, 1e-5, len(w.Edges), 7).toShape()
        else:
            target = self.getTarget(obj, False)
        params = []
        for p in obj.Points:
            params.append(target.Curve.parameter(p))
        if target.isClosed():
            params.append(target.LastParameter)
        obj.NormalizedParameters = KnotVector(params).normalize()

    def onChanged(self, fp, prop):
        # print fp
        if not fp.Edge:
            return
        if prop == "Edge":
            pass
            # self.setEdge( fp)
        if prop == "Target":
            # self.setEdge( fp)
            if fp.Target == "Wire":
                fp.setEditorMode("ParameterFirst", 2)
                fp.setEditorMode("ParameterLast", 2)
            else:
                fp.setEditorMode("ParameterFirst", 0)
                fp.setEditorMode("ParameterLast", 0)

        if prop == "Algorithm":
            if fp.Algorithm in ("Number", "QuasiNumber"):
                fp.setEditorMode("Number", 0)
                fp.setEditorMode("Distance", 2)
                fp.setEditorMode("Deflection", 2)
                fp.setEditorMode("Angular", 2)
                fp.setEditorMode("Curvature", 2)
                fp.setEditorMode("Minimum", 2)
            elif fp.Algorithm == "Distance":
                fp.setEditorMode("Number", 2)
                fp.setEditorMode("Distance", 0)
                fp.setEditorMode("Deflection", 2)
                fp.setEditorMode("Angular", 2)
                fp.setEditorMode("Curvature", 2)
                fp.setEditorMode("Minimum", 2)
            elif fp.Algorithm in ("Deflection", "QuasiDeflection"):
                fp.setEditorMode("Number", 2)
                fp.setEditorMode("Distance", 2)
                fp.setEditorMode("Deflection", 0)
                fp.setEditorMode("Angular", 2)
                fp.setEditorMode("Curvature", 2)
                fp.setEditorMode("Minimum", 2)
            elif fp.Algorithm == "Angular-Curvature":
                fp.setEditorMode("Number", 2)
                fp.setEditorMode("Distance", 2)
                fp.setEditorMode("Deflection", 2)
                fp.setEditorMode("Angular", 0)
                fp.setEditorMode("Curvature", 0)
                fp.setEditorMode("Minimum", 0)
        if prop == "Number":
            if fp.Number <= 1:
                fp.Number = 2
        if prop == "Distance":
            if fp.Distance <= 0.0:
                fp.Distance = 0.0001
        if prop == "Deflection":
            if fp.Deflection <= 0.0:
                fp.Deflection = 0.0001
        if prop == "Angular":
            if fp.Angular <= 0.0:
                fp.Angular = 0.0001
        if prop == "Curvature":
            if fp.Curvature <= 0.0:
                fp.Curvature = 0.0001
        if prop == "Minimum":
            if fp.Minimum < 2:
                fp.Minimum = 2
        if prop == "ParameterFirst":
            if fp.ParameterFirst < self.edgeBounds(fp)[0]:
                fp.ParameterFirst = self.edgeBounds(fp)[0]
        if prop == "ParameterLast":
            if fp.ParameterLast > self.edgeBounds(fp)[1]:
                fp.ParameterLast = self.edgeBounds(fp)[1]


class ViewProviderDisc:
    def __init__(self, vobj):
        vobj.Proxy = self

    def getIcon(self):
        TOOL_ICON = str(
                   Path(__file__).parent.absolute().parent.parent / "images" / "discretize.svg"
                   )
        return (TOOL_ICON)

    def attach(self, vobj):
        self.Object = vobj.Object

    def __getstate__(self):
        return {"name": self.Object.Name}

    def __setstate__(self, state):
        self.Object = FreeCAD.ActiveDocument.getObject(state["name"])
        return None

    def claimChildren(self):
        return [self.Object.Edge[0]]

    def onDelete(self, feature, subelements):
        try:
            self.Object.Edge[0].ViewObject.Visibility = True
        except Exception as err:
            FreeCAD.Console.PrintError("Error in onDelete: {0} \n".format(err))
        return True