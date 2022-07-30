from pathlib import Path

from PySide2 import  QtWidgets
from PySide2.QtWidgets import QMessageBox
from PySide2.QtCore import Qt

import ezdxf

import FreeCAD
import FreeCADGui as Gui
import Draft, Arch

import civiltools_rc


civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'define' / 'create_axes_from_dxf.ui'))
        self.ezdxf_doc = None
        self.x_axis = None
        self.y_axis = None
        self.axis = None
        self.etabs = etabs
        self.fill_levels()
        self.create_connections()

    def create_connections(self):
        self.form.browse.clicked.connect(self.browse)
        self.form.layer_checkbox.clicked.connect(self.layer_clicked)
        self.form.refresh.clicked.connect(self.update_gui)
        self.form.refresh_levels.clicked.connect(self.fill_levels)
        self.form.create_axis.clicked.connect(self.create_axis)
        self.form.export_to_etabs.clicked.connect(self.export_to_etabs)
        self.form.create_columns.clicked.connect(self.create_columns)

    def fill_levels(self):
        if self.etabs is None:
            return
        self.form.levels_list.clear()
        levels_names = self.etabs.story.get_level_names()
        self.form.levels_list.addItems(levels_names)
        lw = self.form.levels_list
        for i in range(lw.count() - 1):
            item = lw.item(i)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)

    def layer_clicked(self):
        if self.form.layer_checkbox.isChecked():
            self.form.layer_combobox.setEnabled(True)
        else:
            self.form.layer_combobox.setEnabled(False)

    def get_layers(self):
        if self.ezdxf_doc is None:
            return
        msp = self.ezdxf_doc.modelspace()
        layers = set()
        for e in msp.query("LINE LWPOLYLINE"):
            layers.add(e.dxf.layer)
        return layers

    def update_gui(self):
        if self.ezdxf_doc is None:
            return
        self.clear_all()
        if FreeCAD.ActiveDocument is None:
            FreeCAD.newDocument('Grids')
        msp = self.ezdxf_doc.modelspace()
        if self.form.layer_checkbox.isChecked():
            layer = self.form.layer_combobox.currentText()
            lines = msp.query(f'LINE LWPOLYLINE[layer=="{layer}"]')
        else:
            lines = msp.query("LINE LWPOLYLINE")
        for line in lines:
            if hasattr(line, 'dxf') and hasattr(line.dxf, 'start'):
                Draft.make_line(tuple(line.dxf.start), tuple(line.dxf.end))
            elif hasattr(line, 'get_points'):
                points = line.get_points()
                p1 = (points[0][0], points[0][1], 0)
                p2 = (points[1][0], points[1][1], 0)
                Draft.make_line(p1, p2)

        FreeCAD.ActiveDocument.recompute()
        Gui.Selection.clearSelection()
        Gui.SendMsgToActiveView("ViewFit")

    def create_columns(self):
        if FreeCAD.ActiveDocument is None:
            FreeCAD.newDocument('Grids')
        self.clear_columns()
        block = self.form.column_block.currentText()
        if block == '':
            return
        msp = self.ezdxf_doc.modelspace()
        width = self.form.col_size.value()
        for i in msp.query(f'INSERT[name=="{block}"]'):
            center = tuple(i.dxf.insert)
            rot = i.dxf.rotation
            col = Arch.makeStructure(length=width, width=width, height = 8 * width)
            col.Placement = FreeCAD.Placement(
            FreeCAD.Vector(*center),
            FreeCAD.Rotation(FreeCAD.Vector(0,0,1),rot))
        FreeCAD.ActiveDocument.recompute()

    def create_axis(self):
        if FreeCAD.ActiveDocument is None:
            return
        x_coordinates, y_coordinates = self.get_xy_coordinates()
        if max((len(x_coordinates), len(y_coordinates))) == 0:
            QMessageBox.Warning(None, 'Error', 'You Must have at least  1 line in X and Y directions.')
            return
        x_style_numbering = self.form.x_style_numbering.currentText()
        y_style_numbering = self.form.y_style_numbering.currentText()
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
        if self.x_axis is None:
            self.x_axis = Arch.makeAxis(len(x_distances), 1000)
            self.x_axis.Label = 'XAxis'
            self.x_axis.ViewObject.LineColor = (0.00,1.00,0.00)
        self.x_axis.ViewObject.FontSize = int(x_length / 10)
        self.x_axis.ViewObject.BubbleSize = self.x_axis.ViewObject.FontSize * 1.5
        self.x_axis.Placement.Base = base
        self.x_axis.ViewObject.NumberingStyle = x_style_numbering
        self.x_axis.Distances = x_distances
        self.x_axis.Length = 1.1 * y_length

        if self.y_axis is None:
            self.y_axis = Arch.makeAxis(len(y_distances), 1000)
            self.y_axis.Label = 'YAxis'
            self.y_axis.ViewObject.LineColor = (1.00,0.00,0.00)
        self.y_axis.ViewObject.FontSize = int(x_length / 10)
        self.y_axis.ViewObject.BubbleSize = self.y_axis.ViewObject.FontSize * 1.5
        self.y_axis.ViewObject.NumberingStyle = y_style_numbering
        self.y_axis.Distances = y_distances
        self.y_axis.Placement.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0, 0, 1), -90)
        self.y_axis.Placement.Base = base + FreeCAD.Vector(0, y_length, 0)
        self.y_axis.Length = 1.1 * x_length
        if self.axis is None:
            self.axis = Arch.makeAxisSystem([self.x_axis, self.y_axis])

    def get_xy_coordinates(self):
        if self.form.selections.isChecked():
            lines = Gui.Selection.getSelection()
        else:
            lines = FreeCAD.ActiveDocument.Objects
        x_coordinates = set()
        y_coordinates = set()
        for line in lines:
            if not hasattr(line, 'Start'):
                continue
            e = line.Shape.Edges[0]
            vecs = e.tangentAt(0)
            if abs(vecs.x) < 0.01 and (0.99 < abs(vecs.y) <1.01):
                x_coordinates.add(line.Start.x)
            elif abs(vecs.y) < 0.01 and (0.99 < abs(vecs.x) <1.01):
                y_coordinates.add(line.Start.y)
        return sorted(x_coordinates), sorted(y_coordinates)

    def clear_all(self):
        doc = FreeCAD.ActiveDocument
        if doc is None:
            return
        for obj in doc.Objects:
            if hasattr(obj, 'IfcType') and obj.IfcType == 'Column':
                continue
            doc.removeObject(obj.Name)
        self.x_axis = None
        self.y_axis = None
        self.axis = None
    
    def clear_columns(self):
        doc = FreeCAD.ActiveDocument
        if doc is None:
            return
        for obj in doc.Objects:
            if hasattr(obj, 'IfcType') and obj.IfcType == 'Column':
                doc.removeObject(obj.Name)

    def get_blocks(self):
        if self.ezdxf_doc is None:
            return
        blocks = set()
        for block in self.ezdxf_doc.blocks:
            blocks.add(block.name)
        return blocks

    def browse(self):
        ext = '.dxf'
        from PySide2.QtWidgets import QFileDialog
        filters = f"{ext[1:]} (*{ext})"
        filename, _ = QFileDialog.getOpenFileName(None, 'select file',
                                                None, filters)
        if not filename:
            return
        if not filename.lower().endswith(ext):
            filename += ext
        self.form.filename.setText(filename)
        try:
            self.ezdxf_doc = ezdxf.readfile(filename)
            layers = self.get_layers()
            self.form.layer_combobox.clear()
            self.form.layer_combobox.addItems(layers)
            blocks = self.get_blocks()
            self.form.column_block.clear()
            self.form.column_block.addItems(blocks)
            if FreeCAD.ActiveDocument is None:
                FreeCAD.newDocument('Grids')
        except IOError:
            print(f"Not a DXF file or a generic I/O error.")
        except ezdxf.DXFStructureError:
            print(f"Invalid or corrupted DXF file.")
        self.update_gui()

    def export_to_etabs(self):
        if self.etabs is None:
            QMessageBox.Warning(None, 'Open ETABS', 'Please open ETABS and run this command again.')
            return

        len_unit = self.form.unit.currentText()
        self.etabs.set_current_unit('N', len_unit)
        self.etabs.unlock_model()
        tab = self.form.tabWidget.currentIndex()
        if tab == 0:
            self.export_axes_to_etabs()
        elif tab == 1:
            self.export_columns_to_etabs()

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
        x_grids = get_axis_data(self.x_axis, 'X')
        for coord, name in x_grids:
            data.extend([g1, 'X (Cartesian)', name, str(coord), '', '', '', '', '', 'End', 'Yes'])
        y_grids = get_axis_data(self.y_axis, 'Y')
        for coord, name in y_grids:
            data.extend([g1, 'Y (Cartesian)', name, str(coord), '', '', '', '', '', 'Start', 'Yes'])
        table_key = 'Grid Definitions - Grid Lines'
        fields = ['Name', 'Grid Line Type', 'ID', 'Ordinate', 'Angle', 'X1', 'Y1', 'X2', 'Y2', 'Bubble Location', 'Visible']
        self.etabs.database.apply_data(table_key, data, fields)
        QMessageBox.information(None, 'Successful', f'{g1} Grid Line Modifided.')

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
                    n += 1
        QMessageBox.information(None, 'Successful', f'{n} columns added to current model.')
                    




        
    def reject(self):
        Gui.Control.closeDialog()

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