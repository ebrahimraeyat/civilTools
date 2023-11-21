from pathlib import Path


import FreeCAD
import FreeCADGui as Gui

# from safe.punch.py_widget import resource_rc

civiltools_path = Path(__file__).parent.parent.parent


class Form:

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'import_export' / 'import_from_dxf.ui'))
        # self.fill_filename()
        self.create_connections()

    def fill_filename(self):
        doc = FreeCAD.ActiveDocument
        name = Path(doc.FileName).with_suffix('.dxf')
        self.form.filename.setText(str(name))

    def create_connections(self):
        self.form.browse.clicked.connect(self.browse)
        self.form.import_button.clicked.connect(self.import_dxf)
        self.form.cancel_pushbutton.clicked.connect(self.accept)

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

    def import_dxf(self):
        filename = self.form.filename.text()
        if not filename:
            return
        doc = FreeCAD.ActiveDocument
        if not doc:
            doc = FreeCAD.newDocument()
        scale = self.form.scale_box.value()
        p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft")
        p.SetFloat("dxfScaling", scale)
        p.SetBool("dxfUseLegacyImporter", True)
        p.GetBool("dxfGetOriginalColors", True)
        
        import importDXF
        importDXF.readPreferences()
        importDXF.getDXFlibs()
        gui = FreeCAD.GuiUp
        if importDXF.dxfReader:
            # groupname = str(Path(filename).name)
            # importgroup = doc.addObject("App::DocumentObjectGroup", groupname)
            # importgroup.Label = groupname
            importDXF.processdxf(doc, filename)
            # for l in layers:
            #     importgroup.addObject(l)
        else:
            importDXF.errorDXFLib(gui)
        self.accept()
        if gui:
            Gui.SendMsgToActiveView("ViewFit")
        
    def getStandardButtons(self):
        return 0           
    
    def accept(self):
        Gui.Control.closeDialog()
