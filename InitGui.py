

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

        # self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Civil tools")), command_list)
        # self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Civil Export")), export_list)
        # self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Civil Draw")), draw_list)
        # self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Civil Assign")), assign_list)
        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("Civil", "civiltools")), civiltools_list)
        # self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Civil")), command_list)
        # self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Export")), export_list)
        # self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Draw")), draw_list)
        # self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Assign")), assign_list)

        # pref_visual_ui_abs_path = str(Path(civilTools_gui.__file__).parent.absolute() / 'ui' / 'preferences-punch_visual.ui')
        # Gui.addPreferencePage(pref_visual_ui_abs_path, "punch")
        # Gui.addIconPath(
        #     str(
        #         Path(civilTools_gui.__file__).parent.absolute()
        #         / "images"
        #         )
        #     )

    # def Activated(self):
    #     if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Civil").GetBool("FirstTime", True):
    #         from DraftGui import todo
    #         todo.delay(Gui.runCommand, "Civil_welcome")


Gui.addWorkbench(CivilToolsWorkbench())