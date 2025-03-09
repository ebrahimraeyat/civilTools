

class CivilToolsWorkbench(Workbench):

    def __init__(self):

        from pathlib import Path
        import civiltoolswelcome
        self.__class__.Icon = str(Path(civiltoolswelcome.__file__).parent / 'images' / 'civiltools.svg')
        self.__class__.MenuText = "civilTools"
        self.__class__.ToolTip = "civilTools Workbench"

    def Initialize(self):
        from pathlib import Path
        from PySide2 import QtCore
        import civilTools_gui

        # command_list = civilTools_gui.command_list
        # export_list = civilTools_gui.export_list
        # draw_list = civilTools_gui.draw_list
        # assign_list = civilTools_gui.assign_list
        civiltools_list = civilTools_gui.civiltools_list
        civiltools_assign = civilTools_gui.civiltools_assign
        civiltools_edit = civilTools_gui.civiltools_edit
        civiltools_tools = civilTools_gui.civiltools_tools
        civiltools_define = civilTools_gui.civiltools_define
        civiltools_import_export = civilTools_gui.civiltools_import_export

        # self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Civil Export")), export_list)
        # self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Civil Draw")), draw_list)
        # self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Civil Assign")), assign_list)
        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("civiltools", "Controls")), civiltools_list[:-5])
        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("civiltools", "Assign")), civiltools_assign[:-1])
        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("civiltools", "civiltools Edit")), civiltools_edit)
        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("civiltools", "Tools")), civiltools_tools[1:])
        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("civiltools", "Define")), civiltools_define)
        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("civiltools", "Import & Export")), civiltools_import_export[:-1])

        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("civiltools", "Controls")), civiltools_list)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("civiltools", "Assign")), civiltools_assign)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("civiltools", "civiltools Edit")), civiltools_edit)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("civiltools", "&Tools")), civiltools_tools)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("civiltools", "Define")), civiltools_define)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("civiltools", "&Help")), civilTools_gui.civiltools_help)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("civiltools", "&View")), civilTools_gui.civiltools_view)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("civiltools", "Import & Export")), civiltools_import_export)
        # self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Export")), export_list)
        # self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Draw")), draw_list)

        pref_visual_ui_abs_path = str(Path(civilTools_gui.__file__).parent.absolute() / 'widgets' / 'preferences-civiltools_visual.ui')
        Gui.addPreferencePage(pref_visual_ui_abs_path, "civilTools")
        Gui.addIconPath(
            str(
                Path(civilTools_gui.__file__).parent.absolute()
                / "images"
                )
            )

    def Activated(self):
        
        from DraftGui import todo
        import check_update

        check_update.check_updates('civilTools')
        if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/civilTools").GetBool("FirstTime", True):
            # from DraftGui import todo
            todo.delay(Gui.runCommand, "civiltools_settings")

        # if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/civilTools").GetBool("show_at_startup", True):
        #     Gui.showPreferences("civilTools", 0)
        
        # FreeCAD.addImportType("CSI ETABS (*.edb *.EDB)", "gui_civiltools.open_etabs")
            
    def splash(self):
        from pathlib import Path
        import shutil
        user_path = Path(FreeCAD.getUserAppDataDir())   
        image = user_path / 'Mod' / 'civilTools' / 'images' / 'civiltools.png'
        if not image.exists():
            return
        splash_path = (user_path / 'Gui' / 'images')
        try:
            splash_path.mkdir(parents=True)
        except FileExistsError:
            pass
        suffix = image.suffix
        splash_image_path = splash_path / f'splash_image{suffix}'
        # check if splash image folder is empty
        hash_md5 = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/civilTools").GetString("splash_hash_md5", '')
        splash_hash_md5 = "85b13cbcb16dca64d61456f56d54e4d3"
        if hash_md5 != splash_hash_md5:
            for i in splash_path.glob("splash_image.*"):
                i.unlink()
            shutil.copy(image, splash_image_path)
            FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/civilTools").SetString("splash_hash_md5", splash_hash_md5)
            FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OSAFE").SetString("splash_hash_md5", splash_hash_md5)
            return


Gui.addWorkbench(CivilToolsWorkbench())
