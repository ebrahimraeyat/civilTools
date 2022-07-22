from pathlib import Path

from PySide2 import  QtWidgets
from PySide2.QtWidgets import QMessageBox

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
        self.freecad_doc = None
        self.x_axis = None
        self.y_axis = None
        self.axis = None
        self.etabs = etabs
        self.create_connections()

    def create_connections(self):
        self.form.browse.clicked.connect(self.browse)
        self.form.layer_checkbox.clicked.connect(self.layer_clicked)
        self.form.refresh.clicked.connect(self.update_gui)
        self.form.create_axis.clicked.connect(self.create_axis)
        self.form.export_to_etabs.clicked.connect(self.export_to_etabs)

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
        for e in msp:
            if e.dxftype() == "LINE":
                layers.add(e.dxf.layer)
        return layers

    def update_gui(self):
        if self.ezdxf_doc is None:
            return
        self.clear_all()
        if self.freecad_doc is None:
            self.freecad_doc = FreeCAD.newDocument('Grids')
        msp = self.ezdxf_doc.modelspace()
        if self.form.layer_checkbox.isChecked():
            layer = self.form.layer_combobox.currentText()
            lines = msp.query(f'LINE[layer=="{layer}"]')
        else:
            lines = msp.query("LINE")
        for line in lines:
            Draft.make_line(tuple(line.dxf.start), tuple(line.dxf.end))
        self.freecad_doc.recompute()
        Gui.Selection.clearSelection()
        Gui.SendMsgToActiveView("ViewFit") 

    def create_axis(self):
        if self.freecad_doc is None:
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
            lines = self.freecad_doc.Objects
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
        if self.freecad_doc is None:
            return
        for obj in self.freecad_doc.Objects:
            self.freecad_doc.removeObject(obj.Name)

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
            if self.freecad_doc is None:
                self.freecad_doc = FreeCAD.newDocument('Grids')
        except IOError:
            print(f"Not a DXF file or a generic I/O error.")
        except ezdxf.DXFStructureError:
            print(f"Invalid or corrupted DXF file.")
        self.update_gui()

    def export_to_etabs(self):
        if self.etabs is None:
            import etabs_obj
            self.etabs = etabs_obj.EtabsModel()
        len_unit = self.form.unit.currentText()
        self.etabs.set_current_unit('N', len_unit)
        self.etabs.unlock_model()
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
        QMessageBox.information(None, 'Successful', f'{g1} Grid Line Modifided. ')
        
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