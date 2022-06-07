from pathlib import Path
import math

import FreeCAD
import ArchComponent

import freecad_funcs


def make_column_section(
        width,
        height,
        N,
        M,
        main_diameter,
        tie_diameter,
        cover,
        main_diameters: list=['14d', '16d', '18d', '20d', '22d', '25d', '28d', '30d'],
        tie_diameters: list=['10d', '12d'],
        pattern_name="C$WidthX$Height_($NX$M)T$RebarSize",
        longitudinal_bar_name='',
        tie_bar_name='',
        tie_bar_space=100,
        n=2,
        m=2,
        concrete_name='',
        fc: str = '25 MPa',
        design_type: str='Check',
    ):
    doc = FreeCAD.ActiveDocument
    obj = doc.addObject("Part::FeaturePython", "Section")
    ConcreteColumnSection(obj)
    obj.B = width
    obj.H = height
    obj.N = N
    obj.M = M
    obj.Diameter = main_diameters
    obj.Tie_Bars_d = tie_diameters
    obj.Diameter = main_diameter
    obj.Tie_Bars_d = tie_diameter
    obj.cover = cover
    obj.Pattern_Name = pattern_name
    obj.Longitudinal_Rebar_Name = longitudinal_bar_name
    obj.Tie_Bars_Name = tie_bar_name
    obj.Tie_Bars_Space = tie_bar_space
    obj.n = n
    obj.m = m
    obj.Concrete_Name = concrete_name
    obj.fc = fc
    obj.Design_type = design_type

    if FreeCAD.GuiUp:
        ViewProviderConcreteColumnSection(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return obj


class ConcreteColumnSection(ArchComponent.Component):
    def __init__(self, obj):
        super().__init__(obj)
        obj.IfcType = "Column"
        self.set_properties(obj)

    def set_properties(self, obj):
        obj.Proxy = self
        self.Type = "ConcreteColumnSection"
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
        if not hasattr(obj, "N"):
            obj.addProperty(
            "App::PropertyInteger",
            "N",
            "Rebars",
            )
        if not hasattr(obj, "M"):
            obj.addProperty(
            "App::PropertyInteger",
            "M",
            "Rebars",
            )
        if not hasattr(obj, "Number"):
            obj.addProperty(
            "App::PropertyInteger",
            "Number",
            "Rebars",
            "",
            16,
            )
        if not hasattr(obj, "Diameter"):
            obj.addProperty(
            "App::PropertyEnumeration",
            "Diameter",
            "Rebars",
            ).Diameter = ['14d', '16d', '18d', '20d', '22d', '25d', '28d', '30d']
        if not hasattr(obj, "Rebar_Percentage"):
            obj.addProperty(
            "App::PropertyFloat",
            "Rebar_Percentage",
            "Rebars",
            "",
            8,
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
        if not hasattr(obj, "Tie_Bars_d"):
            obj.addProperty(
            "App::PropertyEnumeration",
            "Tie_Bars_d",
            "Tie_Bars",
            ).Tie_Bars_d = ['10d', '12d']
        if not hasattr(obj, "Tie_Bars_Space"):
            obj.addProperty(
            "App::PropertyFloat",
            "Tie_Bars_Space",
            "Tie_Bars",
            "",
            8,
            )
        if not hasattr(obj, "n"):
            obj.addProperty(
            "App::PropertyInteger",
            "n",
            "Tie_Bars",
            "",
            8,
            )
        if not hasattr(obj, "m"):
            obj.addProperty(
            "App::PropertyInteger",
            "m",
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
            ).Pattern_Name = '$WidthX$Height'
        if not hasattr(obj, "Section_Name"):
            obj.addProperty(
            "App::PropertyString",
            "Section_Name",
            "Name",
            "",
            8,
            )
        if not hasattr(obj, "Design_type"):
            obj.addProperty(
            "App::PropertyEnumeration",
            "Design_type",
            "",
            ).Design_type = ['Check', 'Design']
        
    def onChanged(self, obj, prop):
        # print(f'on changed: prop = {prop}')

        if (
            prop == "Pattern_Name" and
            hasattr(obj, 'Section_Name')
            ):
            obj.Section_Name = self.get_name(obj)

    def onDocumentRestored(self, obj):
        super().onDocumentRestored(obj)
        self.set_properties(obj)

    def execute(self, obj):
        # print('executed!')
        shape = freecad_funcs.column_shape(
            obj.B.Value,
            obj.H.Value,
            obj.N,
            obj.M,
            int(obj.Diameter.rstrip('d')),
            int(obj.Tie_Bars_d.rstrip('d')),
            obj.cover.Value,
        )
        obj.Shape = shape
        obj.Number = 2 * (obj.N + obj.M) - 4
        obj.Section_Name = self.get_name(obj)
        obj.Rebar_Percentage = self.get_rebar_percentage(obj)

    def get_name(self, obj):
        text = obj.Pattern_Name
        new_text = text.replace(
            '$Width', str(int(obj.B.Value / 10))).replace(
                '$Height', str(int(obj.H.Value / 10))).replace(
                    '$RebarSize', str(obj.Diameter.rstrip('d'))).replace(
                        '$TotalRebars', str(obj.Number)).replace(
                            '$N', str(obj.N)).replace(
                                '$M', str(obj.M)).replace(
                                    '$Fc', str(obj.fc.getValueAs('MPa'))).replace(
                                        '$RebarPercentage', f"{obj.Rebar_Percentage:.1f}"
                                    )
        obj.Label = new_text
        return new_text

    def get_rebar_percentage(self, obj):
        diameter = int(obj.Diameter.rstrip('d'))
        rebar_area = math.pi * int(diameter) ** 2 / 4
        rebar_percentage = rebar_area * obj.Number / (obj.B * obj.H).Value * 100
        return rebar_percentage



class ViewProviderConcreteColumnSection:
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
    
    make_column_section(
        400,
        500,
        4,
        6,
        '25d',
        '10d',
        40,
    )
