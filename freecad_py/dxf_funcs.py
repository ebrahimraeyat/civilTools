import math
if __name__ == "__main__":
    freecad_path = r"G:\Program Files\FreeCAD 0.19\bin"
    import sys
    sys.path.append(freecad_path)
import FreeCAD
import Part, Draft
import DraftVecUtils, DraftGeomUtils, WorkingPlane
from DraftGeomUtils import vec as Vec
from FreeCAD import Vector
from FreeCAD import Console as FCC

import dxfColorMap
import dxfReader

# sets the default working plane if Draft hasn't been started yet
if not hasattr(FreeCAD, "DraftWorkingPlane"):
    plane = WorkingPlane.plane()
    FreeCAD.DraftWorkingPlane = plane

gui = FreeCAD.GuiUp
draftui = None
if gui:
    import FreeCADGui
    try:
        draftui = FreeCADGui.draftToolBar
    except (AttributeError, NameError):
        draftui = None
    from draftutils.translate import translate
    from PySide import QtGui
else:
    def translate(context, txt):
        return txt

p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft")
dxfCreatePart = p.GetBool("dxfCreatePart", True)
dxfCreateDraft = p.GetBool("dxfCreateDraft", False)
dxfCreateSketch = p.GetBool("dxfCreateSketch", False)
dxfDiscretizeCurves = p.GetBool("DiscretizeEllipses", True)
dxfStarBlocks = p.GetBool("dxfstarblocks", False)
dxfMakeBlocks = p.GetBool("groupLayers", False)
dxfJoin = p.GetBool("joingeometry", False)
dxfRenderPolylineWidth = p.GetBool("renderPolylineWidth", False)
dxfImportTexts = p.GetBool("dxftext", False)
dxfImportLayouts = p.GetBool("dxflayouts", False)
dxfImportPoints = p.GetBool("dxfImportPoints", False)
dxfImportHatches = p.GetBool("importDxfHatches", False)
dxfUseStandardSize = p.GetBool("dxfStdSize", False)
dxfGetColors = True
dxfUseLegacyImporter = True
# dxfUseLegacyImporter = p.GetBool("dxfUseLegacyImporter", False)
# dxfGetColors = p.GetBool("dxfGetOriginalColors", False)
dxfUseDraftVisGroups = p.GetBool("dxfUseDraftVisGroups", True)
dxfFillMode = p.GetBool("fillmode", True)
dxfUseLegacyExporter = p.GetBool("dxfUseLegacyExporter", False)
dxfExportBlocks = p.GetBool("dxfExportBlocks", True)
dxfScaling = p.GetFloat("dxfScaling", 1.0)


class ImportDXF:

    def __init__(self, dxf_filename):
        self.drawing = dxfReader.readDXF(dxf_filename)
        self.layerBlocks = {}
        self.blockobjects = {}
        self.blockshapes = {}
        self.layers = []
        self.badobjects = []
        self.getShapes = False
        self.shapes = []
        self.doc = FreeCAD.ActiveDocument

    def drawLine(self, line, forceShape=False):
        """Return a Part shape (Wire or Edge) from a DXF line.

        Parameters
        ----------
        line : drawing.entities
            The DXF object of type `'line'`.

        forceShape : bool, optional
            It defaults to `False`. If it is `True` it will produce a `Part.Edge`,
            otherwise it produces a `Draft Wire`.

        Returns
        -------
        Part::Part2DObject or Part::TopoShape ('Edge')
            The returned object is normally a `Wire`, if the global
            variables `dxfCreateDraft` or `dxfCreateSketch` are set,
            and `forceShape` is `False`.
            Otherwise it produces a `Part.Edge`.

            It returns `None` if it fails.

        See also
        --------
        drawBlock

        To do
        -----
        Use local variables, not global variables.
        """
        if len(line.points) > 1:
            v1 = self.vec(line.points[0])
            v2 = self.vec(line.points[1])
            if not DraftVecUtils.equals(v1, v2):
                try:
                    if (dxfCreateDraft or dxfCreateSketch) and (not forceShape):
                        return Draft.make_wire([v1, v2])
                    else:
                        return Part.LineSegment(v1, v2).toShape()
                except Part.OCCError:
                    self.warn(line)
        return None


    def drawPolyline(self, polyline, forceShape=False, num=None):
        """Return a Part shape (Wire, Face, or Shell) from a DXF polyline.

        It traverses the points of the polyline checking for straight edges,
        and for curvatures (bulges) between two points.
        Then it produces `Part.Edges` and `Part.Arcs`, and decides what to output
        at the end based on the options.

        Parameters
        ----------
        polyline : drawing.entities
            The DXF object of type `'polyline'` or `'lwpolyline'`.

        forceShape : bool, optional
            It defaults to `False`. If it is `True` it will try to produce
            a `Part.Wire`, otherwise it try to produce a `Draft Wire`.

        num : float, optional
            It defaults to `None`. A simple number that identifies this polyline.

        Returns
        -------
        Part::Part2DObject or Part::TopoShape ('Wire', 'Face', 'Shell')
            It returns `None` if it fails producing a shape.

        If the polyline has a `width` and the global variable
        `dxfRenderPolylineWidth` is set, it will try to return a face simulating
        a thick line. If the polyline is closed, it will cut the interior loop
        to produce the a shell.

        If the polyline doesn't have curvatures, and the global variables
        `dxfCreateDraft` or `dxfCreateSketch` are set, and `forceShape` is `False`
        it creates a straight `Draft Wire`.

        If the polyline is closed, and the global variable `dxfFillMode`
        is set, it will return a `Part.Face`, otherwise it will return
        a `Part.Wire`.

        See also
        --------
        drawBlock

        To do
        -----
        Use local variables, not global variables.
        """
        if len(polyline.points) > 1:
            edges = []
            curves = False
            verts = []
            for p in range(len(polyline.points)-1):
                p1 = polyline.points[p]
                p2 = polyline.points[p+1]
                v1 = self.vec(p1)
                v2 = self.vec(p2)
                verts.append(v1)
                if not DraftVecUtils.equals(v1, v2):
                    if polyline.points[p].bulge:
                        curves = True
                        cv = self.calcBulge(v1, polyline.points[p].bulge, v2)
                        if DraftVecUtils.isColinear([v1, cv, v2]):
                            try:
                                edges.append(Part.LineSegment(v1, v2).toShape())
                            except Part.OCCError:
                                self.warn(polyline, num)
                        else:
                            try:
                                edges.append(Part.Arc(v1, cv, v2).toShape())
                            except Part.OCCError:
                                self.warn(polyline, num)
                    else:
                        try:
                            edges.append(Part.LineSegment(v1, v2).toShape())
                        except Part.OCCError:
                            self.warn(polyline, num)
            verts.append(v2)
            if polyline.closed:
                p1 = polyline.points[len(polyline.points)-1]
                p2 = polyline.points[0]
                v1 = self.vec(p1)
                v2 = self.vec(p2)
                cv = self.calcBulge(v1, polyline.points[-1].bulge, v2)
                if not DraftVecUtils.equals(v1, v2):
                    if DraftVecUtils.isColinear([v1, cv, v2]):
                        try:
                            edges.append(Part.LineSegment(v1, v2).toShape())
                        except Part.OCCError:
                            self.warn(polyline, num)
                    else:
                        try:
                            edges.append(Part.Arc(v1, cv, v2).toShape())
                        except Part.OCCError:
                            self.warn(polyline, num)
            if edges:
                try:
                    width = self.rawValue(polyline, 43)
                    if width and dxfRenderPolylineWidth:
                        w = Part.Wire(edges)
                        w1 = w.makeOffset(width/2)
                        if polyline.closed:
                            w2 = w.makeOffset(-width/2)
                            w1 = Part.Face(w1)
                            w2 = Part.Face(w2)
                            if w1.BoundBox.DiagonalLength > w2.BoundBox.DiagonalLength:
                                return w1.cut(w2)
                            else:
                                return w2.cut(w1)
                        else:
                            return Part.Face(w1)
                    elif (dxfCreateDraft or dxfCreateSketch) and (not curves) and (not forceShape):
                        ob = Draft.make_wire(verts)
                        ob.Closed = polyline.closed
                        ob.Placement = self.placementFromDXFOCS(polyline)
                        return ob
                    else:
                        if polyline.closed and dxfFillMode:
                            w = Part.Wire(edges)
                            w.Placement = self.placementFromDXFOCS(polyline)
                            return Part.Face(w)
                        else:
                            w = Part.Wire(edges)
                            w.Placement = self.placementFromDXFOCS(polyline)
                            return w
                except Part.OCCError:
                    self.warn(polyline, num)
        return None
    
    def drawCircle(self, circle, forceShape=False):
        """Return a Part shape (Circle, Edge) from a DXF circle.

        Parameters
        ----------
        circle : drawing.entities
            The DXF object of type `'circle'`. The `'circle'` object is different
            from an `'arc'` because the circle forms a full circumference.

        forceShape : bool, optional
            It defaults to `False`. If it is `True` it will try to produce
            a `Part.Edge`, otherwise it tries to produce a `Draft Circle`.

        Returns
        -------
        Part::Part2DObject or Part::TopoShape ('Edge')
            The returned object is normally a `Draft Circle` with no face,
            if the global variables `dxfCreateDraft` or `dxfCreateSketch` are set,
            and `forceShape` is `False`.
            Otherwise it produces a `Part.Edge`.

            It returns `None` if it fails producing a shape.

        See also
        --------
        drawArc, drawBlock

        To do
        -----
        Use local variables, not global variables.
        """
        v = self.vec(circle.loc)
        curve = Part.Circle()
        curve.Radius = self.vec(circle.radius)
        curve.Center = v
        try:
            if (dxfCreateDraft or dxfCreateSketch) and (not forceShape):
                pl = self.placementFromDXFOCS(circle)
                return Draft.make_circle(circle.radius, pl)
            else:
                return curve.toShape()
        except Part.OCCError:
            self.warn(circle)
        return None

    @classmethod
    def calcBulge(cls, v1, bulge, v2):
        """Calculate intermediary vertex for a curved segment.

        Considering an arc of a circle, it can be defined by two vertices `v1`
        and `v2`, and a `bulge` value that indicates how curved the arc is.
        A `bulge` of 0 is a straight line, while a `bulge` of 1 is the maximum
        curvature, or a semicircle.

        A vertex that is in the curve, equidistant to the two vertices,
        can be found by finding the sagitta of the arc, that is,
        the perpendicular to the chord that goes from `v1` to `v2`.

        It uses the algorithm from http://www.afralisp.net/lisp/Bulges1.htm

        Parameters
        ----------
        v1 : Base::Vector3
            The first point.
        bulge : float
            The bulge is the tangent of 1/4 of the included angle for the arc
            between `v1` and `v2`. A negative `bulge` indicates that the arc
            goes clockwise from `v1` to `v2`. A `bulge` of 0 indicates
            a straight segment, and a `bulge` of 1 is a semicircle.
        v2 : Base::Vector3
            The second point.

        Returns
        -------
        Base::Vector3
            The new point betwwen `v1` and `v2`.
        """
        chord = v2.sub(v1)
        sagitta = (bulge * chord.Length)/2
        perp = chord.cross(Vector(0, 0, 1))
        startpoint = v1.add(chord.multiply(0.5))
        if not DraftVecUtils.isNull(perp):
            perp.normalize()
        endpoint = perp.multiply(sagitta)
        return startpoint.add(endpoint)

    def placementFromDXFOCS(self, ent):
        """Return the placement of an object from AutoCAD's OCS.

        In AutoCAD DXF's the points of each entity are expressed in terms
        of the entity's object coordinate system (OCS).
        Then to determine the entity's position in 3D space,
        what is needed is a 3D vector defining the Z axis of the OCS,
        and the elevation value over it.

        It uses `WorkingPlane.alignToPointAndAxis()` to align the working plane
        to the origin and to `ent.extrusion` (the plane's `axis`).
        Then it gets the global coordinates of the entity
        by using `WorkingPlane.getGlobalCoords()`
        and either `ent.elevation` (Z coordinate) or `ent.loc` a `(x,y,z)` tuple.

        Parameters
        ----------
        ent : A DXF entity
            It could be of several types, like `lwpolyline`, `polyline`,
            and others, and with `ent.extrusion`, `ent.elevation`
            or `ent.loc` attributes.

        Returns
        -------
        Base::Placement
            A placement, comprised of a `Base` (`Base::Vector3`),
            and a `Rotation` (`Base::Rotation`).

        See also
        --------
        WorkingPlane.alignToPointAndAxis, WorkingPlane.getGlobalCoords
        """
        draftWPlane = FreeCAD.DraftWorkingPlane
        draftWPlane.alignToPointAndAxis(Vector(0.0, 0.0, 0.0),
                                        self.vec(ent.extrusion), 0.0)
        # Object Coordinate Systems (OCS)
        # http://docs.autodesk.com/ACD/2011/ENU/filesDXF/WS1a9193826455f5ff18cb41610ec0a2e719-7941.htm
        # Arbitrary Axis Algorithm
        # http://docs.autodesk.com/ACD/2011/ENU/filesDXF/WS1a9193826455f5ff18cb41610ec0a2e719-793d.htm#WSc30cd3d5faa8f6d81cb25f1ffb755717d-7ff5
        # Riferimenti dell'algoritmo dell'asse arbitrario in italiano
        # http://docs.autodesk.com/ACD/2011/ITA/filesDXF/WS1a9193826455f5ff18cb41610ec0a2e719-7941.htm
        # http://docs.autodesk.com/ACD/2011/ITA/filesDXF/WS1a9193826455f5ff18cb41610ec0a2e719-793d.htm#WSc30cd3d5faa8f6d81cb25f1ffb755717d-7ff5
        if (draftWPlane.axis == FreeCAD.Vector(1.0, 0.0, 0.0)):
            draftWPlane.u = FreeCAD.Vector(0.0, 1.0, 0.0)
            draftWPlane.v = FreeCAD.Vector(0.0, 0.0, 1.0)
        elif (draftWPlane.axis == FreeCAD.Vector(-1.0, 0.0, 0.0)):
            draftWPlane.u = FreeCAD.Vector(0.0, -1.0, 0.0)
            draftWPlane.v = FreeCAD.Vector(0.0, 0.0, 1.0)
        else:
            if ((abs(ent.extrusion[0]) < (1.0 / 64.0)) and (abs(ent.extrusion[1]) < (1.0 / 64.0))):
                draftWPlane.u = FreeCAD.Vector(0.0, 1.0, 0.0).cross(draftWPlane.axis)
            else:
                draftWPlane.u = FreeCAD.Vector(0.0, 0.0, 1.0).cross(draftWPlane.axis)
            draftWPlane.u.normalize()
            draftWPlane.v = draftWPlane.axis.cross(draftWPlane.u)
            draftWPlane.v.normalize()
            draftWPlane.position = Vector(0.0, 0.0, 0.0)
            draftWPlane.weak = False

        pl = FreeCAD.Placement()
        pl = draftWPlane.getPlacement()
        if ((ent.type == "lwpolyline") or (ent.type == "polyline")):
            pl.Base = draftWPlane.getGlobalCoords(self.vec([0.0, 0.0, ent.elevation]))
        else:
            pl.Base = draftWPlane.getGlobalCoords(self.vec(ent.loc))
        return pl

    def warn(self, dxfobject, num=None):
        """Print a warning that the DXF object couldn't be imported.

        Also add the object to the global list `badobjects`.

        Parameters
        ----------
        dxfobject : drawing.entities
            The DXF object that couldn't be imported.

        num : float, optional
            It defaults to `None`. A simple number that identifies
            the given `dxfobject`.

        To do
        -----
        Use local variables, not global variables.
        """
        print("dxf: couldn't import ", dxfobject, " (", num, ")")
        self.badobjects.append(dxfobject)

    @classmethod
    def getColor(cls):
        """Get the Draft color defined in the Draft toolbar or preferences.

        Returns
        -------
        tuple of 4 floats
            Return the `(r, g, b, 0.0)` tuple with the colors defined
            in the Draft toolbar, if the graphical user interface is active.
            Otherwise, return the tuple with the color
            of the `DefaultShapeLineColor` in the parameter database.
        """
        if gui and draftui:
            r = float(draftui.color.red()/255.0)
            g = float(draftui.color.green()/255.0)
            b = float(draftui.color.blue()/255.0)
            return (r, g, b, 0.0)
        else:
            p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View")
            c = p.GetUnsigned("DefaultShapeLineColor", 0)
            r = float(((c >> 24) & 0xFF)/255)
            g = float(((c >> 16) & 0xFF)/255)
            b = float(((c >> 8) & 0xFF)/255)
            return (r, g, b, 0.0)

    @classmethod
    def isBrightBackground(cls):
        """Check if the current viewport's background is a bright color.

        It considers the values of `BackgroundColor` for a solid background,
        or a combination of `BackgroundColor2` and `BackgroundColor3`
        for a gradient background from the parameter database.

        Returns
        -------
        bool
            Returns `True` if the value of the color is larger than 128,
            which is considered light; otherwise it is considered dark
            and returns `False`.
        """
        p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View")
        if p.GetBool("Gradient"):
            c1 = p.GetUnsigned("BackgroundColor2")
            c2 = p.GetUnsigned("BackgroundColor3")
            r1 = float((c1 >> 24) & 0xFF)
            g1 = float((c1 >> 16) & 0xFF)
            b1 = float((c1 >> 8) & 0xFF)
            r2 = float((c2 >> 24) & 0xFF)
            g2 = float((c2 >> 16) & 0xFF)
            b2 = float((c2 >> 8) & 0xFF)
            v1 = Vector(r1, g1, b1)
            v2 = Vector(r2, g2, b2)
            v = v2.sub(v1)
            v.multiply(0.5)
            cv = v1.add(v)
        else:
            c1 = p.GetUnsigned("BackgroundColor")
            r1 = float((c1 >> 24) & 0xFF)
            g1 = float((c1 >> 16) & 0xFF)
            b1 = float((c1 >> 8) & 0xFF)
            cv = Vector(r1, g1, b1)
        value = cv.x*.3 + cv.y*.59 + cv.z*.11
        if value < 128:
            return False
        else:
            return True

    

    @classmethod
    def getMultiplePoints(cls, entity):
        """Scan the given entity (paths, leaders, etc.) for multiple points.

        Parameters
        ----------
        entity : drawing.entities
            A DXF entity in the `drawing` data obtained from `processdxf`.

        Returns
        -------
        list of Base::Vector3
            The list of points (vectors).
            Each point has three coordinates `(X,Y,Z)`.
            If the original point only had two, the third coordinate
            is set to zero `(X,Y,0)`.
        """
        pts = []
        for d in entity.data:
            if d[0] == 10:
                pts.append([d[1]])
            elif d[0] == 20:
                pts[-1].append(d[1])
        pts.reverse()
        points = []
        for p in pts:
            points.append(Vector(p[0], p[1], 0))
        return points

    @classmethod
    def rawValue(cls, entity, code):
        """Return the value of a DXF code in an entity section.

        Parameters
        ----------
        entity : drawing.entities
            A DXF entity in the `drawing` data obtained from `processdxf`.
        code : int
            A numerical value of the code.

        Returns
        -------
        float or str
            The value corresponding to the code. It may be numeric or a string.
        """
        value = None
        for pair in entity.data:
            if pair[0] == code:
                value = pair[1]
        return value

    def addToBlock(self, obj, layer):
        """Add the given object to the layer in the global dictionary.

        It searches for `layer` in the global dictionary `layerBlocks`.
        If found, it appends the `obj` to the `layer`;
        otherwise, it adds the `layer` to `layerBlocks` first,
        and then adds `obj`.

        Parameters
        ----------
        obj : Part.Shape or App::DocumentObject
            Any shape or Draft object previously created from a DXF file.
        layer : str
            The name of a layer to which `obj` is added.

        To do
        -----
        Use local variables, not global variables.
        """
        if layer in self.layerBlocks:
            self.layerBlocks[layer].append(obj)
        else:
            self.layerBlocks[layer] = [obj]

    def addObject(self, shape, name="Shape", layer=None):
        """Adds a new object to the document, with the given name and layer.

        Parameters
        ----------
        shape : Part.Shape or Part::Feature
            The simple Part.Shape or Draft object previously created
            from an entity in a DXF file.

        name : str, optional
            It defaults to "Shape". The name of the new document object.

        layer : App::FeaturePython or App::DocumentObjectGroup, optional
            It defaults to `None`.
            The `Draft Layer` (`App::FeaturePython`)
            or simple group (`App::DocumentObjectGroup`)
            to which the new object will be added.

        Returns
        -------
        Part::Feature or Part::Part2DObject
            If the `shape` is a simple `Part.Shape`, it will be encapsulated
            inside a `Part::Feature` object and this will be returned.
            Otherwise, it is assumed it is already a Draft object
            (`Part::Part2DObject`) and will just return this.

            It applies the text and line color by calling `formatObject()`
            before returning the new object.
        """
        if isinstance(shape, Part.Shape):
            newob = self.doc.addObject("Part::Feature", name)
            newob.Shape = shape
        else:
            newob = shape
        if layer:
            lay = self.locateLayer(layer)
            # For old style layers, which are just groups
            if hasattr(lay, "addObject"):
                lay.addObject(newob)
            # For new Draft Layers
            elif hasattr(lay, "Proxy") and hasattr(lay.Proxy, "addObject"):
                lay.Proxy.addObject(lay, newob)
        # formatObject(newob)
        return newob

    def locateLayer(self, wantedLayer, color=None, drawstyle=None):
        """Return layer group and create it if needed.

        This function iterates over a global list named `layers`, which is
        defined in `processdxf`.

        If no layers are found it looks for the global `dxfUseDraftVisGroup`
        variable defined in `readPreferences`, and creates a new `Draft Layer`
        with the specified color.

        Otherwise it creates a group (`App::DocumentObjectGroup`)
        to use as a layer container.

        Parameters
        ----------
        wantedLayer : str
            The name of a layer to search in the global `layers` list.

        color : tuple of four floats, optional
            It defaults to `None`.
            A tuple with color information `(r,g,b,a)`, where each value
            is a float between 0 and 1.

        Returns
        -------
        App::FeaturePython or App::DocumentObjectGroup
            If the `wantedLayer` is found in the global list of layers,
            it is returned.
            Otherwise, a new layer or group is created and returned.

            If the global variable `dxfUseDraftVisGroup` is set,
            it creates a `Draft Layer` (`App::FeaturePython`).
            Otherwise, it creates a simple group (`App::DocumentObjectGroup`).

        See also
        --------
        Draft.make_layer

        To do
        -----
        Use local variables, not global variables.
        """
        # layers is a global variable.
        # It should probably be passed as an argument.
        wantedLayerName = self.decodeName(wantedLayer)
        for l in self.layers:
            if wantedLayerName == l.Label:
                return l
        if dxfUseDraftVisGroups:
            print(f'wantedLayer = {wantedLayer}, type={type(wantedLayer)}')
            newLayer = Draft.make_layer(name=wantedLayer,
                                        line_color=color,
                                        draw_style=drawstyle)
            print(f'newlayer is {newLayer}')
        else:
            print(f'wantedLayer else = {wantedLayer}, type={type(wantedLayer)}')
            newLayer = self.doc.addObject("App::DocumentObjectGroup", wantedLayer)
        newLayer.Label = wantedLayerName
        self.layers.append(newLayer)
        return newLayer

    @classmethod
    def decodeName(cls, name):
        """Decode the encoded name into utf8 or latin1.

        Parameters
        ----------
        name : str
            The string to decode.

        Returns
        -------
        str
            The decoded string in utf8, latin1, or the original `name`
            if the decoding was not needed, for example,
            when using Python 3.
        """
        try:
            decodedName = (name.decode("utf8"))
        except UnicodeDecodeError:
            try:
                decodedName = (name.decode("latin1"))
            except UnicodeDecodeError:
                print("dxf: error: couldn't determine character encoding")
                decodedName = name
        except AttributeError:
            # this is python3 (nothing to do)
            decodedName = name
        return decodedName

    @classmethod
    def drawLayerBlock(cls, objlist):
        """Return a Draft Block (compound) from the given object list.

        Parameters
        ----------
        objlist : list
            A list of Draft objects or Part.shapes.

        Returns
        -------
        Part::Part2DObject or Part::TopoShape ('Compound')
            If the global variables `dxfCreateDraft` or `dxfCreateSketch` are set,
            and no element in `objlist` is a `Part.Shape`,
            it will try to return a `Draft Block`.
            Otherwise, it will try to return a `Part.Compound`.

            It returns `None` if it fails producing a shape.

        To do
        -----
        Use local variables, not global variables.
        """
        obj = None
        try:
            obj = Part.makeCompound(objlist)
        except Part.OCCError:
            pass
        return obj

    def formatObject(self, obj, dxfobj=None):
        """Apply text and line color to an object from a DXF object.

        This function only works when the graphical user interface is loaded
        as it needs access to the `ViewObject` attribute of the objects.

        If `dxfobj` and the global variable `dxfGetColors` exist
        the `TextColor` and `LineColor` of `obj` will be set to the color
        indicated by the global dictionary
        `dxfColorMap.color_map[dxfobj.color_index]`.

        If the global `dxfBrightBackground` is set, it will set the `LineColor`
        to black.

        If no `dxfobj` is given, `TextColor` and `LineColor`
        are set to the global variable `dxfDefaultColor`.

        Parameters
        ----------
        obj : App::DocumentObject
            Object that will use the DXF color.

        dxfobj : drawing.entities, optional
            It defaults to `None`. DXF object from which the color will be taken.

        To do
        -----
        Use local variables, not global variables.
        """
        if dxfGetColors and dxfobj and hasattr(dxfobj, "color_index"):
            if hasattr(obj.ViewObject, "TextColor"):
                if dxfobj.color_index == 256:
                    cm = self.getGroupColor(dxfobj)[:3]
                else:
                    cm = dxfColorMap.color_map[dxfobj.color_index]
                obj.ViewObject.TextColor = (cm[0], cm[1], cm[2])
            elif hasattr(obj.ViewObject, "LineColor"):
                if dxfobj.color_index == 256:
                    cm = self.getGroupColor(dxfobj)
                elif (dxfobj.color_index == 7) and dxfBrightBackground:
                    cm = [0.0, 0.0, 0.0]
                else:
                    cm = dxfColorMap.color_map[dxfobj.color_index]
                obj.ViewObject.LineColor = (cm[0], cm[1], cm[2], 0.0)
        else:
            if hasattr(obj.ViewObject, "TextColor"):
                obj.ViewObject.TextColor = dxfDefaultColor
            elif hasattr(obj.ViewObject, "LineColor"):
                obj.ViewObject.LineColor = dxfDefaultColor

    def getGroupColor(self, dxfobj, index=False):
        """Get the color of the layer.

        It searches the global variable `drawing.tables`,
        created in `processdxf`, for a `layer`; then iterates on the data,
        and if the layer name matches the layer of `dxfobj`, it will try
        to return the color of its layer.

        It searches the global variable `dxfBrightBackground` to determine
        if it should return black, or a color from the global
        `dxfColorMap.color_map` dictionary.

        Parameters
        ----------
        dxfobj : Part::Feature
            An imported DXF object.

        index : bool, optional
            It defaults to `False`. If it is `True` it will return the layer's
            color; otherwise it will check the global variable
            `dxfBrightBackground`, and return black or a mapped color.

        Returns
        -------
        list of 3 floats
            The layer's color as a list `[r, g, b]`, black `[0, 0, 0]`
            or the mapped color `dxfColorMap.color_map[color]`.

        To do
        -----
        Use local variables, not global variables.
        """
        name = dxfobj.layer
        for table in self.drawing.tables.get_type("table"):
            if table.name == "layer":
                for l in table.get_type("layer"):
                    if l.name == name:
                        if index:
                            return l.color
                        else:
                            if (l.color == 7) and dxfBrightBackground:
                                return [0.0, 0.0, 0.0]
                            else:
                                if isinstance(l.color, int):
                                    if l.color > 0:
                                        return dxfColorMap.color_map[l.color]
        return [0.0, 0.0, 0.0]

    @classmethod
    def prec(cls):
        """Return the current Draft precision level."""
        return 0
        # return Draft.getParam("precision", 6)

    @classmethod
    def vec(cls, pt):
        """Return a rounded and scaled Vector from a DXF point.

        Parameters
        ----------
        pt : Base::Vector3, or list of three numerical values, or float, or int
            A point with three coordinates `(x, y, z)`,
            or just a single numerical value.

        Returns
        -------
        Base::Vector3 or float
            Each of the components of the vector, or the single numerical value,
            is rounded to the precision defined by `prec`,
            and scaled by the amount of the global variable `dxfScaling`.

        To do
        -----
        Use local variables, not global variables.
        """
        if isinstance(pt, (int, float)):
            if dxfScaling != 1:
                pt = pt * dxfScaling
            v = round(pt, cls.prec())
        else:
            v = Vector(*pt)
            if dxfScaling != 1:
                v.multiply(dxfScaling)
            v = Vector(round(v.x, cls.prec()),
                    round(v.y, cls.prec()),
                    round(v.z, cls.prec()))
        return v


    def drawInsert(self, insert, num=None, clone=False):
        """Return a Part Shape (Compound, Clone) from a DXF insert.

        It searches for `insert.block` in `blockobjects`
        or `blockshapes`, and returns a clone or a copy of the compound,
        with transformations applied: rotation, translation (movement),
        and scaling.

        If the global variable `dxfImportTexts` is available
        it will check the attributes of `insert` and add those text attributes
        to their own layers with `addText`.

        Parameters
        ----------
        insert : drawing.entities
            The DXF object of type `'insert'`.

        num : float, optional
            It defaults to `None`. A simple number that identifies
            the given block being drawn, if it is not a clone.

        clone : bool, optional
            It defaults to `False`. If it is `True` it will try to produce
            and return a `Draft Clone` of the `'insert.block'` contained
            in the global dictionary `blockobjects`.

            Otherwise, it will try to return a copy of the shape
            of the `'insert.block'` contained in the global dictionary
            `blockshapes`, or created from the `drawing.blocks.data`
            with `drawBlock()`.

        Returns
        -------
        Part::TopoShape ('Compound') or
        Part::Part2DObject or Part::PartFeature (`Draft Clone`)
            The returned object is normally a copy of the `Part.Compound`
            extracted from `blockshapes` or created with `drawBlock()`.

            If `clone` is `True` then it will try returning
            a `Draft Clone` from the `'insert.block'` contained
            in the global dictionary `blockobjects`.
            It returns `None` if `insert.block` isn't in `blockobjects`.

            In any of these two cases, it will try to apply the
            insert transformations: rotation, translation (movement),
            and scaling.

        See also
        --------
        drawBlock

        To do
        -----
        Use local variables, not global variables.
        """
        if dxfImportTexts:
            attrs = self.attribs(insert)
            for a in attrs:
                self.addText(a, attrib=True)
        if clone:
            if insert.block in self.blockobjects:
                newob = Draft.make_clone(self.blockobjects[insert.block])
                tsf = FreeCAD.Matrix()
                rot = math.radians(insert.rotation)
                pos = self.vec(insert.loc)
                tsf.move(pos)
                tsf.rotateZ(rot)
                sc = insert.scale
                sc = self.vec([sc[0], sc[1], 0])
                newob.Placement = FreeCAD.Placement(tsf)
                newob.Scale = sc
                return newob
            else:
                shape = None
        else:
            if insert in self.blockshapes:
                shape = self.blockshapes[insert.block].copy()
            else:
                shape = None
                for b in self.drawing.blocks.data:
                    if b.name == insert.block:
                        shape = self.drawBlock(b, num)
            if shape:
                bb = shape.BoundBox
                width = bb.XLength
                height = bb.YLength
                pos = self.vec(insert.loc)
                rot = math.radians(insert.rotation)
                tsf = FreeCAD.Matrix()
                if self.check_rectangle(shape.Edges):
                    print(f'{insert.block} is rectangle\n')
                    e = shape.Edges[0]
                    v = e.tangentAt(0)
                    if v.x == 0:
                        rot = 0
                        e = shape.Edges[1]
                    else:
                        rot = math.atan(v.y / v.x)
                    width = e.Length
                    height = 0
                    for e in shape.Edges:
                        if e.Length != width:
                            height = e.Length
                            break
                    if height == 0:
                        height = width
                else:
                    tsf.rotateZ(rot)
                scale = insert.scale
                # for some reason z must be 0 to work
                tsf.scale(scale[0], scale[1], 0)
                try:
                    shape = shape.transformGeometry(tsf)
                except Part.OCCError:
                    tsf.scale(scale[0], scale[1], 0)
                    try:
                        shape = shape.transformGeometry(tsf)
                    except Part.OCCError:
                        print("importDXF: unable to apply insert transform:", tsf)
                shape.translate(pos)
                return shape, width, height, rot
        return None

    def drawBlock(self, blockref, num=None, createObject=False):
        """Return a Part Shape (Compound) from a DXF block reference.

        It inspects the `blockref.entities` for objects of types `'line'`,
        `'polyline'`, `'lwpolyline'`, `'arc'`, `'circle'`, `'insert'`,
        `'solid'`, and `'spline'`.
        If they are found they create shapes with `drawLine`,
        `drawMesh` or `drawPolyline`, `drawArc`, `drawCircle`, `drawInsert`,
        `drawSolid`, `drawSpline`, and adds all shapes to a list.
        Then it makes a compound of all those shapes.

        In the case of entities of type `'text'` and `'mtext'`
        it will only process the entities if the global variable
        `dxfImportTexts` exist, and `dxfImportLayouts` exists
        or if the DXF code 67 doesn't indicate an empty space (empty text).
        Then it will use `addText` and add the found text to its proper
        layer.

        Parameters
        ----------
        blockref : drawing.blocks.data
            The DXF block data.

        num : float, optional
            It defaults to `None`. A simple number that identifies
            the given `blockref`.

        createObject : bool, optional
            It defaults to `False`. If it is `True` it will try to produce
            and return a `'Part::Feature'` with the compound
            as its shape attribute.
            Otherwise, just return the `Part.Compound`.

        Returns
        -------
        Part::TopoShape ('Compound') or Part::Feature
            The returned object is normally a `Part.Compound`
            created from the list of all `Part.Shapes` created from
            the `blockref` entities, if `createObject` is `False`.
            Otherwise, it will return a `'Part::Feature'` document object
            with the compound as its shape attribute.

            In the first case, it will add the compound shape
            to the global dictionary `blockshapes`.
            In the latter case, it will add the `'Part::Feature'` object
            to the global dictionary `blockobjects`.

            It returns `None` if the global variable `dxfStarBlocks`
            doesn't exist, if the `blockref.entities.data` is empty,
            or if it fails producing the compound shape.

        See also
        --------
        `drawLine`, `drawMesh`, `drawPolyline`, `drawArc`, `drawCircle`,
        `drawInsert`, `drawSolid`, `drawSpline`, `addText`.

        To do
        -----
        Use local variables, not global variables.
        """
        if not dxfStarBlocks and blockref.name[0] == '*':
                return None
        if len(blockref.entities.data) == 0:
            print("skipping empty block ", blockref.name)
            return None
        # print("creating block ", blockref.name,
        #       " containing ", len(blockref.entities.data), " entities")
        shapes = []
        for line in blockref.entities.get_type('line'):
            s = self.drawLine(line, forceShape=True)
            if s:
                shapes.append(s)
        for polyline in blockref.entities.get_type('polyline'):
            s = self.drawPolyline(polyline, forceShape=True)
            if s:
                shapes.append(s)
        for polyline in blockref.entities.get_type('lwpolyline'):
            s = self.drawPolyline(polyline, forceShape=True)
            if s:
                shapes.append(s)
        # for arc in blockref.entities.get_type('arc'):
        #     s = drawArc(arc, forceShape=True)
        #     if s:
        #         shapes.append(s)
        for circle in blockref.entities.get_type('circle'):
            s = self.drawCircle(circle, forceShape=True)
            if s:
                shapes.append(s)
        for insert in blockref.entities.get_type('insert'):
            # print("insert ",insert," in block ",insert.block[0])
            if dxfStarBlocks or insert.block[0] != '*':
                s = self.drawInsert(insert)[0]
                if s:
                    shapes.append(s)
        # for solid in blockref.entities.get_type('solid'):
        #     s = drawSolid(solid)
        #     if s:
        #         shapes.append(s)
        # for spline in blockref.entities.get_type('spline'):
        #     s = drawSpline(spline, forceShape=True)
        #     if s:
        #         shapes.append(s)
        # for text in blockref.entities.get_type('text'):
        #     if dxfImportTexts:
        #         if dxfImportLayouts or (not rawValue(text, 67)):
        #             addText(text)
        # for text in blockref.entities.get_type('mtext'):
        #     if dxfImportTexts:
        #         if dxfImportLayouts or (not rawValue(text, 67)):
        #             print("adding block text", text.value, " from ", blockref)
        #             addText(text)
        try:
            shape = Part.makeCompound(shapes)
        except Part.OCCError:
            self.warn(blockref)
        if shape:
            self.blockshapes[blockref.name] = shape
            if createObject:
                newob = self.doc.addObject("Part::Feature", blockref.name)
                newob.Shape = shape
                self.blockobjects[blockref.name] = newob
                return newob
            return shape
        return None

    @classmethod
    def get_edges_angle(cls, edge1, edge2):
        """get_edges_angle(edge1, edge2): returns a angle between two edges."""
        vec1 = Vec(edge1)
        vec2 = Vec(edge2)
        angle = vec1.getAngle(vec2)
        angle = math.degrees(angle)
        return angle

    @classmethod
    def check_rectangle(cls, edges):
        """check_rectangle(edges=[]): This function checks whether the given form
        rectangle or not. It will return True when edges form rectangular shape or
        return False when edges not form a rectangular shape."""
        if len(edges) != 4:
            return False
        angles = [
            round(cls.get_edges_angle(edges[0], edges[1])),
            round(cls.get_edges_angle(edges[0], edges[2])),
            round(cls.get_edges_angle(edges[0], edges[3])),
        ]
        if angles.count(90) == 2 and (
            angles.count(180) == 1 or angles.count(0) == 1
        ):
            return True
        else:
            return False

    def create_layer(self):
        if hasattr(self.drawing, "tables"):
            for table in self.drawing.tables.get_type("table"):
                for layer in table.get_type("layer"):
                    name = layer.name
                    color = tuple(dxfColorMap.color_map[layer.color])
                    drawstyle = "Solid"
                    lt = self.rawValue(layer, 6)
                    if "DASHED" in lt.upper():
                        drawstyle = "Dashed"
                    elif "HIDDEN" in lt.upper():
                        drawstyle = "Dotted"
                    if ("DASHDOT" in lt.upper()) or ("CENTER" in lt.upper()):
                        drawstyle = "Dashdot"
                    self.locateLayer(name, color, drawstyle)
        else:
            self.locateLayer("0", (0.0, 0.0, 0.0), "Solid")


    def draw_hatches(self):
        # Draw hatches
        hatches = self.drawing.entities.get_type("hatch")
        if hatches:
            FCC.PrintMessage("drawing " + str(len(hatches)) + " hatches...\n")
        for hatch in hatches:
            if dxfImportLayouts or (not rawValue(hatch, 67)):
                points = self.getMultiplePoints(hatch)
                if len(points) > 1:
                    lay = self.rawValue(hatch, 8)
                    points = points[:-1]
                    newob = None
                    if dxfCreatePart or dxfMakeBlocks:
                        points.append(points[0])
                        s = Part.makePolygon(points)
                        if dxfMakeBlocks:
                            self.addToBlock(s, lay)
                        else:
                            newob = self.addObject(s, "Hatch", lay)
                            if gui:
                                self.formatObject(newob, hatch)
                    else:
                        newob = Draft.make_wire(points)
                        self.locateLayer(lay).addObject(newob)
                        if gui:
                            self.formatObject(newob, hatch)

    def draw_line(self):
        # Draw lines
        lines = self.drawing.entities.get_type("line")
        if lines:
            FCC.PrintMessage("drawing " + str(len(lines)) + " lines...\n")
        for line in lines:
            if dxfImportLayouts or (not self.rawValue(line, 67)):
                shape = self.drawLine(line)
                if shape:
                    if dxfCreateSketch:
                        FreeCAD.ActiveDocument.recompute()
                        if dxfMakeBlocks or dxfJoin:
                            if sketch:
                                shape = Draft.make_sketch(shape,
                                                            autoconstraints=True,
                                                            addTo=sketch)
                            else:
                                shape = Draft.make_sketch(shape,
                                                            autoconstraints=True)
                                sketch = shape
                        else:
                            shape = Draft.make_sketch(shape,
                                                        autoconstraints=True)
                    elif dxfJoin or self.getShapes:
                        if isinstance(shape, Part.Shape):
                            self.shapes.append(shape)
                        else:
                            self.shapes.append(shape.Shape)
                    elif dxfMakeBlocks:
                        self.addToBlock(shape, line.layer)
                    else:
                        newob = self.addObject(shape, "Line", line.layer)
                        if gui:
                            self.formatObject(newob, line)

    # Draw polylines
    def draw_polyline(self):
        pls = self.drawing.entities.get_type("lwpolyline")
        pls.extend(self.drawing.entities.get_type("polyline"))
        polylines = []
        meshes = []
        for p in pls:
            if hasattr(p, "flags"):
                if p.flags in [16, 64]:
                    meshes.append(p)
                else:
                    polylines.append(p)
            else:
                polylines.append(p)
        if polylines:
            FCC.PrintMessage("drawing " + str(len(polylines)) + " polylines...\n")
        num = 0
        for polyline in polylines:
            if dxfImportLayouts or (not self.rawValue(polyline, 67)):
                shape = self.drawPolyline(polyline, num)
                if shape:
                    if dxfCreateSketch:
                        if isinstance(shape, Part.Shape):
                            t = FreeCAD.ActiveDocument.addObject("Part::Feature",
                                                                    "Shape")
                            t.Shape = shape
                            shape = t
                        FreeCAD.ActiveDocument.recompute()
                        if dxfMakeBlocks or dxfJoin:
                            if sketch:
                                shape = Draft.make_sketch(shape,
                                                            autoconstraints=True,
                                                            addTo=sketch)
                            else:
                                shape = Draft.make_sketch(shape,
                                                            autoconstraints=True)
                                sketch = shape
                        else:
                            shape = Draft.make_sketch(shape,
                                                        autoconstraints=True)
                    elif dxfJoin or self.getShapes:
                        if isinstance(shape, Part.Shape):
                            self.shapes.append(shape)
                        else:
                            self.shapes.append(shape.Shape)
                    elif dxfMakeBlocks:
                        self.addToBlock(shape, polyline.layer)
                    else:
                        if self.check_rectangle(shape.Edges):
                            e = shape.Edges[0]
                            v = e.tangentAt(0)
                            if v.x == 0:
                                rot = 0
                                e = shape.Edges[1]
                            else:
                                rot = math.degrees(math.atan(v.y / v.x))
                            width = e.Length
                            height = 0
                            for e in shape.Edges:
                                if e.Length != width:
                                    height = e.Length
                                    break
                            if height == 0:
                                height = width
                            newob = self.addObject(shape, "Polyline", polyline.layer)
                            newob.addProperty('App::PropertyLength', 'width', 'Geometry')
                            newob.width = width
                            newob.addProperty('App::PropertyLength', 'height', 'Geometry')
                            newob.height = height
                            newob.addProperty('App::PropertyAngle', 'rotation', 'Geometry')
                            newob.rotation = rot
                            newob.addProperty('App::PropertyString', 'name', 'Base')
                            newob.name = 'column'
                            if gui:
                                self.formatObject(newob, polyline)
                num += 1


    # Join lines, polylines and arcs if needed
    def join_dxf(self):
        if dxfJoin and self.shapes:
            FCC.PrintMessage("Joining geometry...\n")
            edges = []
            for s in self.shapes:
                edges.extend(s.Edges)
            if len(edges) > (100):
                FCC.PrintMessage(str(len(edges)) + " edges to join\n")
                if FreeCAD.GuiUp:
                    d = QtGui.QMessageBox()
                    d.setText("Warning: High number of entities to join (>100)")
                    d.setInformativeText("This might take a long time "
                                            "or even freeze your computer. "
                                            "Are you sure? You can also disable "
                                            "the 'join geometry' setting in DXF "
                                            "import preferences")
                    d.setStandardButtons(QtGui.QMessageBox.Ok
                                            | QtGui.QMessageBox.Cancel)
                    d.setDefaultButton(QtGui.QMessageBox.Cancel)
                    res = d.exec_()
                    if res == QtGui.QMessageBox.Cancel:
                        FCC.PrintMessage("Aborted\n")
                        # return
            shapes = DraftGeomUtils.findWires(edges)
            for s in shapes:
                self.addObject(s)
    
    def draw_circles(self):
        circles = self.drawing.entities.get_type("circle")
        if circles:
            FCC.PrintMessage("drawing " + str(len(circles))+" circles...\n")
        for circle in circles:
            if dxfImportLayouts or (not self.rawValue(circle, 67)):
                shape = self.drawCircle(circle)
                if shape:
                    if dxfCreateSketch:
                        FreeCAD.ActiveDocument.recompute()
                        if dxfMakeBlocks or dxfJoin:
                            if sketch:
                                shape = Draft.make_sketch(shape,
                                                        autoconstraints=True,
                                                        addTo=sketch)
                            else:
                                shape = Draft.make_sketch(shape,
                                                        autoconstraints=True)
                                sketch = shape
                        else:
                            shape = Draft.make_sketch(shape,
                                                    autoconstraints=True)
                    elif dxfMakeBlocks:
                        self.addToBlock(shape, circle.layer)
                    elif self.getShapes:
                        if isinstance(shape, Part.Shape):
                            self.shapes.append(shape)
                        else:
                            self.shapes.append(shape.Shape)
                    else:
                        newob = self.addObject(shape, "Circle", circle.layer)
                        if gui:
                            self.formatObject(newob, circle)


    # Draw blocks
    def draw_block(self):
        inserts = self.drawing.entities.get_type("insert")
        if not dxfStarBlocks:
            # FCC.PrintMessage("skipping *blocks...\n")
            newinserts = []
            for i in inserts:
                if dxfImportLayouts or (not self.rawValue(i, 67)):
                    if i.block[0] != '*':
                        newinserts.append(i)
            inserts = newinserts
        if inserts:
            FCC.PrintMessage("drawing " + str(len(inserts)) + " blocks...\n")
            num = 0
            for insert in inserts:
                if (dxfCreateDraft or dxfCreateSketch) and not dxfMakeBlocks:
                    shape, width, height, rotation = self.drawInsert(insert, num, clone=True)
                else:
                    shape, width, height, rotation = self.drawInsert(insert, num)
                if shape:
                    if dxfMakeBlocks:
                        self.addToBlock(shape, insert.layer)
                    else:
                        block_name = insert.block
                        newob = self.addObject(shape, "Block." + block_name,
                                            insert.layer)
                        newob.addProperty('App::PropertyLength', 'width', 'Geometry')
                        newob.width = width
                        newob.addProperty('App::PropertyLength', 'height', 'Geometry')
                        newob.height = height
                        newob.addProperty('App::PropertyAngle', 'rotation', 'Geometry')
                        newob.rotation = math.degrees(rotation)
                        newob.addProperty('App::PropertyString', 'name', 'Base')
                        newob.name = block_name
                        if gui:
                            self.formatObject(newob, insert)
                num += 1


# if dxfMakeBlocks:
#     print("creating layerblocks...")
#     for k, l in layerBlocks.items():
#         shape = drawLayerBlock(l)
#         if shape:
#             newob = addObject(shape, k)

# del layerBlocks

# # Hide block objects, if any
# for k, o in blockobjects.items():
#     if o.ViewObject:
#         o.ViewObject.hide()
# del blockobjects

dxfBrightBackground = ImportDXF.isBrightBackground()
dxfDefaultColor = ImportDXF.getColor()


if __name__ == '__main__':
    FreeCAD.newDocument()
    FreeCAD.ActiveDocument.saveAs('ali.FCStd')
    p = r"E:\alaki\plans\Drawing1.dxf"
    dxf = ImportDXF(p)
    # dxf.create_layer()
    dxf.draw_block()
    print("")

