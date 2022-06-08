from pathlib import Path

import FreeCAD

import freecad_funcs


def make_beam_section(
        width,
        height,
        cover: float = 65,
        pattern_name="B$WidthX$Height",
        longitudinal_bar_name='',
        tie_bar_name='',
        concrete_name='',
        fc: str = '25 MPa',
    ):
    doc = FreeCAD.ActiveDocument
    obj = doc.addObject("Part::FeaturePython", "Section")
    ConcreteBeamSection(obj)
    obj.B = width
    obj.H = height
    obj.cover = cover
    obj.Pattern_Name = pattern_name
    obj.Longitudinal_Rebar_Name = longitudinal_bar_name
    obj.Tie_Bars_Name = tie_bar_name
    obj.Concrete_Name = concrete_name
    obj.fc = fc

    if FreeCAD.GuiUp:
        ViewProviderConcreteBeamSection(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return obj


class ConcreteBeamSection:
    def __init__(self, obj):
        self.set_properties(obj)

    def set_properties(self, obj):
        obj.Proxy = self
        self.Type = "ConcreteBeamSection"
        if not hasattr(obj, "B"):
            obj.addProperty(
            "App::PropertyLength",
            "B",
            "Dimentions",
            )
        if not hasattr(obj, "H"):
            obj.addProperty(
            "App::PropertyLength",
            "H",
            "Dimentions",
            )
        if not hasattr(obj, "cover"):
            obj.addProperty(
            "App::PropertyLength",
            "cover",
            "Dimentions",
            )
        if not hasattr(obj, "Longitudinal_Rebar_Name"):
            obj.addProperty(
            "App::PropertyString",
            "Longitudinal_Rebar_Name",
            "Rebars",
            "",
            8,
            )
        if not hasattr(obj, "Tie_Bars_Name"):
            obj.addProperty(
            "App::PropertyString",
            "Tie_Bars_Name",
            "Tie_Bars",
            "",
            8,
            )
        if not hasattr(obj, "fc"):
            obj.addProperty(
            "App::PropertyPressure",
            "fc",
            "Concrete",
            "",
            8,
            )
        if not hasattr(obj, "Concrete_Name"):
            obj.addProperty(
            "App::PropertyString",
            "Concrete_Name",
            "Concrete",
            "",
            8,
            )
        if not hasattr(obj, "Pattern_Name"):
            obj.addProperty(
            "App::PropertyString",
            "Pattern_Name",
            "Name",
            "",
            8,
            ).Pattern_Name = 'B$WidthX$Height'
        if not hasattr(obj, "Section_Name"):
            obj.addProperty(
            "App::PropertyString",
            "Section_Name",
            "Name",
            "",
            8,
            )
        
    def onChanged(self, obj, prop):
        if (
            prop == "Pattern_Name" and
            hasattr(obj, 'Section_Name')
            ):
            obj.Section_Name = self.get_name(obj)

    def onDocumentRestored(self, obj):
        self.set_properties(obj)

    def execute(self, obj):
        shape = freecad_funcs.rectangle_face(
            obj.B.Value,
            obj.H.Value,
        )
        obj.Shape = shape
        obj.Section_Name = self.get_name(obj)

    def get_name(self, obj):
        text = obj.Pattern_Name
        new_text = text.replace(
            '$Width', str(int(obj.B.Value / 10))).replace(
                '$Height', str(int(obj.H.Value / 10))).replace(
                                    '$Fc', str(obj.fc.getValueAs('MPa'))
                                    )
        obj.Label = new_text
        return new_text


class ViewProviderConcreteBeamSection:
    def __init__(self, vobj):
        vobj.Proxy = self

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def setEdit(self, vobj, mode=0):
        for obj in FreeCAD.ActiveDocument.Objects:
            obj.ViewObject.hide()
        vobj.show()
        return True

    def getIcon(self):
        return str(Path(__file__).parent.parent / "images" / "frame_sections.svg")

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


if __name__ == "__main__":
    
    make_beam_section(
        400,
        500,
        40,
    )
