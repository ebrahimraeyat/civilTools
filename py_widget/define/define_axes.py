from pathlib import Path
import math

from PySide2 import  QtWidgets
from PySide2.QtWidgets import QMessageBox, QFileDialog
from PySide2.QtCore import Qt


import FreeCAD
import FreeCADGui as Gui
import Arch

from freecad_py import dxf_funcs

import civiltools_rc


civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'define' / 'create_axes_from_dxf.ui'))
        self.dxf_filename = None
        self.etabs = etabs
        self.dxf_content = None
        self.fill_levels()
        self.create_connections()

    def set_dxf_scale(self):
        p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft")
        scale = self.form.unit_number.value()
        p.SetFloat("dxfScaling", scale)
    
    def set_scale(self):
        unit = self.form.unit.currentText()
        units = {
                'm': 1000,
                'cm': 10,
                'mm': 1,
                }
        scale = units[unit]
        self.form.unit_number.setValue(scale)
        # p.SetBool("dxfUseLegacyImporter", True)
        # p.GetBool("dxfGetOriginalColors", True)

    def create_connections(self):
        self.form.columns_from.currentIndexChanged.connect(self.column_from_changed)
        self.form.browse.clicked.connect(self.browse)
        self.form.create_axis.clicked.connect(self.create_axis)
        self.form.export_to_etabs.clicked.connect(self.export_to_etabs)
        self.form.create_columns.clicked.connect(self.create_columns)
        self.form.referesh.clicked.connect(self.fill_levels)
        self.form.cancel_button.clicked.connect(self.reject)
        self.form.unit.currentIndexChanged.connect(self.set_scale)

    def column_from_changed(self):
        read_from = self.form.columns_from.currentText()
        self.form.column_names.clear()
        if read_from == 'Block':
            blocks = self.get_blocks()
            self.form.column_names.addItems(blocks)
            self.form.column_names.setEnabled(True)
        elif read_from == 'Hatch':
            self.form.column_names.setEnabled(False)
            # hatches = self.get_hatches()
            # self.form.column_names.addItems(hatches)

    def fill_levels(self):
        if not self.etabs.success:
            import find_etabs
            etabs, filename = find_etabs.find_etabs(run=False, backup=True)
            if (
                not etabs.success or
                filename is None
                ):
                return
            else:
                self.etabs = etabs
        self.form.levels_list.clear()
        levels_names = self.etabs.story.get_level_names()
        self.form.levels_list.addItems(levels_names)
        lw = self.form.levels_list
        for i in range(lw.count() - 1):
            item = lw.item(i)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)


    def import_dxf_in_freecad(self):
        if self.dxf_filename is None:
            return
        if FreeCAD.ActiveDocument is None:
            FreeCAD.newDocument('Grids')
        self.set_dxf_scale()
        import importlib
        importlib.reload(dxf_funcs)
        draw_line = self.form.lines.isChecked()
        draw_polyline = draw_line
        draw_block = self.form.blocks.isChecked()
        draw_hatches = self.form.hatches.isChecked()
        self.dxf_content = dxf_funcs.ImportDXF(self.dxf_filename)
        self.dxf_content.create_layer()
        if draw_block:
            self.dxf_content.draw_block()
        if draw_line:
            self.dxf_content.draw_line()
        if draw_polyline:
            self.dxf_content.draw_polyline()
        if draw_hatches:
            pass
        FreeCAD.ActiveDocument.recompute()
        Gui.Selection.clearSelection()
        Gui.SendMsgToActiveView("ViewFit")

    def create_columns(self):
        if self.form.columns_from.currentText() == 'Block':
            block_name = self.form.column_names.currentText()
        elif self.form.columns_from.currentText() == 'Hatch':
            block_name = 'column'
        for obj in FreeCAD.ActiveDocument.Objects:
            if  (hasattr(obj, 'rotation') and
                hasattr(obj, 'width') and
                hasattr(obj, 'height') and
                hasattr(obj, 'name')
            ):
                if block_name and obj.name != block_name:
                    continue
                else:
                    v = obj.Shape.BoundBox.Center
                    center = FreeCAD.Vector(
                        round(v.x, 0),
                        round(v.y, 0),
                        round(v.z, 0)
                        )
                    col = Arch.makeStructure(
                        length=obj.width,
                        width=obj.height,
                        height = 8 * obj.width)
                    col.Placement = FreeCAD.Placement(
                    center,
                    FreeCAD.Rotation(FreeCAD.Vector(0,0,1),obj.rotation))
        FreeCAD.ActiveDocument.recompute()

    def create_axis(self):
        if FreeCAD.ActiveDocument is None:
            return
        x_coordinates, y_coordinates = self.get_xy_coordinates()
        # if max((len(x_coordinates), len(y_coordinates))) == 0:
        #     QMessageBox.Warning(None, 'Error', 'You Must have at least  1 line in X and Y directions.')
        #     return
        x_style_numbering = self.form.x_style_numbering.currentText()
        if x_style_numbering == '1,2,3':
            y_style_numbering = 'A,B,C'
        else:
            y_style_numbering = '1,2,3'
        x_length = max(x_coordinates) - min(x_coordinates)
        y_length = max(y_coordinates) - min(y_coordinates)
        base = FreeCAD.Vector(min(x_coordinates), min(y_coordinates), 0)
        x_distances = [0]
        y_distances = [0]
        if len(x_coordinates) > 1:
            for i, j in zip(x_coordinates[:-1], x_coordinates[1:]):
                dist = j - i
                x_distances.append(dist)
        if len(y_coordinates) > 1:
            for i, j in zip(y_coordinates[-2::-1], y_coordinates[-1:0:-1]):
                dist = j - i
                y_distances.append(dist)
        x_axis = Arch.makeAxis(len(x_distances), 1000)
        x_axis.Label = 'XAxis'
        x_axis.ViewObject.LineColor = (0.00,1.00,0.00)
        x_axis.ViewObject.FontSize = int(x_length / 15)
        x_axis.ViewObject.BubbleSize = x_axis.ViewObject.FontSize * 1.5
        x_axis.Placement.Base = base
        x_axis.ViewObject.NumberingStyle = x_style_numbering
        x_axis.Distances = x_distances
        x_axis.Length = 1.1 * y_length

        y_axis = Arch.makeAxis(len(y_distances), 1000)
        y_axis.Label = 'YAxis'
        y_axis.ViewObject.LineColor = (1.00,0.00,0.00)
        y_axis.ViewObject.FontSize = int(x_length / 15)
        y_axis.ViewObject.BubbleSize = y_axis.ViewObject.FontSize * 1.5
        y_axis.ViewObject.NumberingStyle = y_style_numbering
        y_axis.Distances = y_distances
        y_axis.Placement.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0, 0, 1), -90)
        y_axis.Placement.Base = base + FreeCAD.Vector(0, y_length, 0)
        y_axis.Length = 1.1 * x_length
        Arch.makeAxisSystem([x_axis, y_axis])

    def get_xy_coordinates(self):
        x_coordinates = set()
        y_coordinates = set()
        doc = FreeCAD.ActiveDocument
        for obj in doc.Objects:
            if hasattr(obj, 'IfcType') and obj.IfcType == 'Column':
                base = obj.Placement.Base
                x = round(base.x, -1)
                y = round(base.y, -1)
                x_coordinates.add(x)
                y_coordinates.add(y)
                obj.Placement.Base.x = x
                obj.Placement.Base.y = y
        if self.form.selections.isChecked():
            lines = Gui.Selection.getSelection()
            for line in lines:
                e = line.Shape.Edges[0]
                vecs = e.tangentAt(0)
                if abs(vecs.x) < 0.01 and (0.99 < abs(vecs.y) <1.01):
                    x_coordinates.add(round(e.BoundBox.XMin, -1))
                elif abs(vecs.y) < 0.01 and (0.99 < abs(vecs.x) <1.01):
                    y_coordinates.add(round(e.BoundBox.YMin, -1))
        return sorted(x_coordinates), sorted(y_coordinates)

    
    def clear_columns(self):
        doc = FreeCAD.ActiveDocument
        if doc is None:
            return
        for obj in doc.Objects:
            if hasattr(obj, 'IfcType') and obj.IfcType == 'Column':
                doc.removeObject(obj.Name)

    def get_blocks(self):
        blocks = set()
        if self.dxf_content is None:
            if FreeCAD.ActiveDocument is None:
                return
            else:
                return
        inserts = self.dxf_content.drawing.entities.get_type("insert")   
        for i in inserts:
            blocks.add(i.block)
        return blocks
    
    def get_hatches(self):
        hatches = set()
        if self.ezdxf_doc is None:
            if FreeCAD.ActiveDocument is None:
                return
            else:
                return
        msp = self.ezdxf_doc.modelspace()  
        q = msp.query("HATCH")      
        for hatch in q:
            hatches.add(hatch.dxf.pattern_name)
        return hatches

    def browse(self):
        ext = '.dxf'
        filters = f"{ext[1:]} (*{ext})"
        filename, _ = QFileDialog.getOpenFileName(None, 'select file',
                                                None, filters)
        if not filename:
            return
        if not filename.lower().endswith(ext):
            filename += ext
        FreeCAD.newDocument()
        self.dxf_filename = filename
        self.import_dxf_in_freecad()
        self.column_from_changed()

    def export_to_etabs(self):
        ret = self.show_etabs_warning()
        if not ret:
            return

        self.etabs.set_current_unit('N', 'mm')
        self.etabs.unlock_model()
        g1 = self.export_axes_to_etabs()
        n = self.export_columns_to_etabs()
        msg = f'{n} columns added to current model and {g1} Grid Line Modifided.'
        QMessageBox.information(None, 'Successful', msg)
        self.etabs.SapModel.File.Save()

    def export_axes_to_etabs(self):
        grids = self.etabs.SapModel.GridSys.GetNameList()[1]
        g1 = None
        if grids:
            for grid in grids:
                if self.etabs.SapModel.GridSys.GetGridSysType(grid)[0] == 'Cartesian':
                    g1 = grid
                    break
        if g1 is None:
            self.etabs.SapModel.GridSys.SetGridSys('G1', 0, 0, 0)
            g1 = 'G1'
        data = []
        x_axis, y_axis = get_xy_axis()
        if x_axis:
            x_grids = get_axis_data(x_axis, 'X')
            for coord, name in x_grids:
                data.extend([g1, 'X (Cartesian)', name, str(coord), '', '', '', '', '', 'End', 'Yes'])
        if y_axis:
            y_grids = get_axis_data(y_axis, 'Y')
            for coord, name in y_grids:
                data.extend([g1, 'Y (Cartesian)', name, str(coord), '', '', '', '', '', 'Start', 'Yes'])
        table_key = 'Grid Definitions - Grid Lines'
        fields = ['Name', 'Grid Line Type', 'ID', 'Ordinate', 'Angle', 'X1', 'Y1', 'X2', 'Y2', 'Bubble Location', 'Visible']
        self.etabs.database.apply_data(table_key, data, fields)
        return g1

    def export_columns_to_etabs(self):
        doc = FreeCAD.ActiveDocument
        if doc is None:
            return
        import math
        n = 0
        level_names = []
        all_level_names = []
        lw = self.form.levels_list
        for i in range(lw.count()):
            item = lw.item(i)
            all_level_names.append(item.text())
            if item.checkState() == Qt.Checked:
                level_names.append(item.text())
        for obj in doc.Objects:
            if hasattr(obj, 'IfcType') and obj.IfcType == 'Column':
                x, y, _ = tuple(obj.Placement.Base)
                rot = math.degrees(obj.Placement.Rotation.Angle)
                for level_name in level_names:
                    i = all_level_names.index(level_name)
                    next_level_name = all_level_names[i + 1]
                    level = self.etabs.SapModel.Story.GetElevation(level_name)[0]
                    next_level = self.etabs.SapModel.Story.GetElevation(next_level_name)[0]
                    name = self.etabs.SapModel.FrameObj.AddByCoord(x, y, level, x, y, next_level)[0]
                    self.etabs.SapModel.FrameObj.SetLocalAxes(name, rot)
                    insertion_point = self.etabs.SapModel.FrameObj.GetInsertionPoint(name)
                    insertion_point[0] = 10
                    self.etabs.SapModel.FrameObj.SetInsertionPoint(name, *insertion_point[:-1])
                    n += 1
        return n
        
    def reject(self):
        Gui.Control.closeDialog()

    def getStandardButtons(self):
        return 0

    def show_etabs_warning(self):
        if not self.etabs.success:
            QMessageBox.warning(None, 'Open ETABS', 'Please open ETABS and Press referesh button.')
            return False
        return True


def get_xy_axis():
    x_axis = None
    y_axis = None
    for obj in FreeCAD.ActiveDocument.Objects:
        if (
            hasattr(obj, 'Distances') and
            hasattr(obj, 'Length') and
            hasattr(obj, 'Angles')
        ):
            degree = math.degrees(obj.Placement.Rotation.Angle)
            if degree == 0 or degree == 180:
                if x_axis is None:
                    x_axis = obj
            elif degree == 90 or degree == 270:
                if y_axis is None:
                    y_axis = obj
    return x_axis, y_axis

def get_axis_data(obj, direction='X'):
    data = []
    num = obj.ViewObject.StartNumber - 1
    for e in obj.Shape.Edges:
        axdata = []
        if direction == 'X':
            axdata.append(e.Vertexes[0].Point.x)
        elif direction == 'Y':
            axdata.append(e.Vertexes[0].Point.y)
        if obj.ViewObject:
            axdata.append(obj.ViewObject.Proxy.getNumber(obj.ViewObject,num))
        data.append(axdata)
        num += 1
    return data