

class CivilToolsWorkbench(Workbench):

    def __init__(self):

        from pathlib import Path
        import civiltoolswelcome
        self.__class__.Icon = str(Path(civiltoolswelcome.__file__).parent.absolute() / 'images' / 'civil-engineering.png')
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
        civiltools_tools = civilTools_gui.civiltools_tools
        civiltools_define = civilTools_gui.civiltools_define

        # self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Civil Export")), export_list)
        # self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Civil Draw")), draw_list)
        # self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Civil Assign")), assign_list)
        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("civiltools", "Controls")), civiltools_list)
        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("civiltools", "Assign")), civiltools_assign)
        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("civiltools", "Tools")), civiltools_tools[1:])
        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("civiltools", "Define")), civiltools_define)

        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("civiltools", "Controls")), civiltools_list)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("civiltools", "Assign")), civiltools_assign)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("civiltools", "&Tools")), civiltools_tools)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("civiltools", "Define")), civiltools_define)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("civiltools", "&Help")), civilTools_gui.civiltools_help)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("civiltools", "&View")), civilTools_gui.civiltools_view)
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


Gui.addWorkbench(CivilToolsWorkbench())
