from pathlib import Path

from PySide2.QtWidgets import QMessageBox
from numpy import isin

import FreeCAD

import etabs_obj

def open(filename):
    # import os
    # docname = os.path.splitext(os.path.basename(filename))[0]
    # doc = FreeCAD.newDocument(docname)
    # doc.Label = docname
    insert(filename)
    # return doc


def insert(filename):
    param = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/civilTools")
    use_etabs = param.GetBool('use_etabs', False)
    software_exe_path = param.GetString('etabs_exe_path', '')
    if (
        use_etabs and
        Path(software_exe_path).exists()
        ):
        attach_to_instance = False
    else:
        attach_to_instance = True
    etabs = etabs_obj.EtabsModel(
                attach_to_instance=attach_to_instance,
                backup = False,
                model_path = Path(filename),
                software_exe_path=software_exe_path,
            )
    FreeCAD.Base.etabs = etabs

def open_browse(
        ext: str = '.EDB',
        ):
    from PySide2.QtWidgets import QFileDialog
    filters = f"{ext[1:]} (*{ext})"
    filename, _ = QFileDialog.getOpenFileName(None, 'select file',
                                            None, filters)
    if not filename:
        return None
    if not filename.upper().endswith(ext):
        filename += ext
    return filename

def find_etabs(
    run=False,
    backup=False,
    ):
    '''
    try to find etabs in this manner:
    1- FreeCAD.etabs if FreeCAD.etabs.success
    2- connect to open ETABS model
    3- try to open etabs if user set the etabs_exe_path

    run : if True it runs the model
    backup: if True it backup from the main file
    '''
    etabs = None
    filename = None
    com_error = False
    import _ctypes
    if (
        hasattr(FreeCAD.Base, 'etabs') and
        hasattr(FreeCAD.Base.etabs, 'SapModel')
        # FreeCAD.Base.etabs.success
        ):
        try:
            FreeCAD.Base.etabs.SapModel.Story
            FreeCAD.Base.etabs.SapModel.GetModelFilename()
            FreeCAD.Base.etabs.SapModel.FrameObj.GetNameList()
            etabs = FreeCAD.Base.etabs
        except _ctypes.COMError:
            FreeCAD.Base.etabs = None
            QMessageBox.warning(None, 'ETABS', 'Please Close ETABS and FreeCAD and try again.')
            com_error = True
    if etabs is None and not com_error:
        etabs = etabs_obj.EtabsModel(backup=False)
        if not etabs.success:
            param = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/civilTools")
            etabs_exe = param.GetString('etabs_exe_path', '')
            if Path(etabs_exe).exists():
                etabs = etabs_obj.EtabsModel(
                    attach_to_instance=False,
                    backup = False,
                    model_path = None,
                    software_exe_path=etabs_exe,
                    )
    if etabs and hasattr(etabs, 'SapModel'):
        try:
            name = FreeCAD.Base.etabs.SapModel.GetModelFilename()
            if name.upper().endswith('.EDB'):
                filename = name
        except:
            filename = None
    if etabs is None and not com_error:
        if (QMessageBox.question(
            None,
            'ETABS',
            '''Please Open ETABS Software.
If ETABS is now open, close it and run this command again. 
You must specify the ETABS.exe path from "Edit / Preferences / civilTools / General Tab".
Do you want to specify ETABS.exe path?''',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
            ) == QMessageBox.Yes
            ):
            import FreeCADGui
            FreeCADGui.showPreferences("civilTools", 0)
    elif filename is None and not com_error:
        filename = open_browse()
        if filename is None:
            QMessageBox.warning(None, 'ETABS', 'Please Open ETABS Model and Run this command again.')
        elif hasattr(etabs, 'success') and etabs.success:
            etabs.SapModel.File.OpenFile(str(filename))
    if (
        run and
        etabs is not None and
        filename is not None and
        hasattr(etabs, 'SapModel') and
        not etabs.SapModel.GetModelIsLocked()
        ):
        QMessageBox.information(
            None,
            'Run ETABS Model',
            'Model did not run and needs to be run. It takes some times.')
        progressbar = FreeCAD.Base.ProgressIndicator()
        progressbar.start("Run ETABS Model ... ", 2)
        progressbar.next(True)
        etabs.run_analysis()
        progressbar.stop()
    if (
        etabs is not None and
        not com_error
        ):
        FreeCAD.Base.etabs = etabs
        if backup:
            FreeCAD.Base.etabs.backup_model()
    if isinstance(filename, str) and Path(filename).exists():
        filename = Path(filename)
    return FreeCAD.Base.etabs, filename
