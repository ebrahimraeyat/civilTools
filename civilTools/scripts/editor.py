# -*- coding: utf-8 -*-
"""
Program:
    Editor
    (LibreEngineering)
    editor.py

Author:
    Alex Borisov <>

Copyright (c) 2010-2012 Alex Borisov

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

####################################################################
##
## Copyright (C) 2010 Hans-Peter Jansen <hpj@urpla.net>.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
####################################################################

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
import resources

class Editor(QMainWindow):
    def __init__(self, file_name = None, win_title = None, parent = None):
        super(Editor, self).__init__(parent)

        self.script_path = sys.path[0]
        self.save_path = ""
        self.read_settings()

        self.parent = parent
        self.file_name = file_name
        self.win_title = win_title

        self.win_size = QSize(800, 800)

        self.icon_win = QIcon(":/main_resources/icons/libreengineering.png")
        self.icon_bold = QIcon(":/main_resources/icons/main/bold.png")
        self.icon_center = QIcon(":/main_resources/icons/main/center.png")
        self.icon_copy = QIcon(":/main_resources/icons/main/copy.png")
        self.icon_cut = QIcon(":/main_resources/icons/main/cut.png")
        self.icon_font = QIcon(":/main_resources/icons/main/font.png")
        self.icon_italic = QIcon(":/main_resources/icons/main/italic.png")
        self.icon_just = QIcon(":/main_resources/icons/main/just.png")
        self.icon_left = QIcon(":/main_resources/icons/main/left.png")
        self.icon_new = QIcon(":/main_resources/icons/main/clear.png")
        self.icon_open = QIcon(":/main_resources/icons/main/open.png")
        self.icon_paste = QIcon(":/main_resources/icons/main/paste.png")
        self.icon_pdf = QIcon(":/main_resources/icons/main/pdf.png")
        self.icon_print = QIcon(":/main_resources/icons/main/print.png")
        self.icon_quit = QIcon(":/main_resources/icons/main/quit.png")
        self.icon_redo = QIcon(":/main_resources/icons/main/redo.png")
        self.icon_right = QIcon(":/main_resources/icons/main/right.png")
        self.icon_save = QIcon(":/main_resources/icons/main/save.png")
        self.icon_saveas = QIcon(":/main_resources/icons/main/saveas.png")
        self.icon_underline = QIcon(":/main_resources/icons/main/underline.png")
        self.icon_undo = QIcon(":/main_resources/icons/main/undo.png")
        self.icon_about = QIcon(":/main_resources/icons/main/about.png")
        self.icon_qt = QIcon(":/main_resources/icons/qt.png")

        self.setWindowIcon(self.icon_win)
        self.resize(self.win_size)
        self.setWindowTitle("Calculation Results - " + self.win_title)

        self.setup_file_actions()
        self.setup_edit_actions()
        self.setup_text_actions()
        self.setup_other_actions()
        self.setup_style_actions()

        self.text_edit = QTextEdit(self)
        self.text_edit.currentCharFormatChanged.connect(self.current_char_format_changed)
        self.text_edit.cursorPositionChanged.connect(self.cursor_position_changed)
        self.setCentralWidget(self.text_edit)
        self.text_edit.setFocus()
        self.set_current_filename()
        self.font_changed(self.text_edit.font())
        self.color_changed(self.text_edit.textColor())
        self.alignment_changed(self.text_edit.alignment())
        self.text_edit.document().modificationChanged.connect(self.action_save.setEnabled)
        self.text_edit.document().modificationChanged.connect(self.setWindowModified)
        self.text_edit.document().undoAvailable.connect(self.action_undo.setEnabled)
        self.text_edit.document().redoAvailable.connect(self.action_redo.setEnabled)
        self.text_edit.document().setDocumentMargin(10)

        self.action_save.setEnabled(self.text_edit.document().isModified())
        self.action_undo.setEnabled(self.text_edit.document().isUndoAvailable())
        self.action_redo.setEnabled(self.text_edit.document().isRedoAvailable())
        self.action_undo.triggered.connect(self.text_edit.undo)
        self.action_redo.triggered.connect(self.text_edit.redo)
        self.action_cut.setEnabled(False)
        self.action_copy.setEnabled(False)
        self.action_cut.triggered.connect(self.text_edit.cut)
        self.action_copy.triggered.connect(self.text_edit.copy)
        self.action_paste.triggered.connect(self.text_edit.paste)
        self.text_edit.copyAvailable.connect(self.action_cut.setEnabled)
        self.text_edit.copyAvailable.connect(self.action_copy.setEnabled)
        QApplication.clipboard().dataChanged.connect(self.clipboard_data_changed)

        index = self.combo_font.findText("Arial Unicode MS")
        if index != -1:
            self.combo_font.setCurrentIndex(index)

        self.load(file_name)

    def read_settings(self):
        if sys.platform == "win32":
            settings = QSettings(self.script_path + "/scripts/editor.ini", QSettings.IniFormat)
        else:
            settings = QSettings(QDir.homePath() + "/.LibreEngineering/editor.conf", QSettings.NativeFormat)
        settings.beginGroup("init_settings")
        self.save_path = settings.value("save_path", QDir.homePath()).toString()
        settings.endGroup()

    def write_settings(self):
        if sys.platform == "win32":
            settings = QSettings(self.script_path + "/scripts/editor.ini", QSettings.IniFormat)
        else:
            settings = QSettings(QDir.homePath() + "/.LibreEngineering/editor.conf", QSettings.NativeFormat)
        settings.beginGroup("init_settings")
        settings.setValue("save_path", self.save_path)
        settings.endGroup()

    def closeEvent(self, e):
        if self.maybe_save():
            e.accept()
        else:
            e.ignore()
        self.write_settings()

    def setup_file_actions(self):
        tb = QToolBar(self)
        tb.setWindowTitle("File Actions")
        self.addToolBar(tb)

        menu = QMenu("&File", self)
        self.menuBar().addMenu(menu)

        self.action_open = QAction(QIcon(self.icon_open),
                                    "&Open...", self,
                                    shortcut=QKeySequence.Open,
                                    triggered=self.file_open)
        tb.addAction(self.action_open)
        menu.addAction(self.action_open)
        menu.addSeparator()

        self.action_save = QAction(QIcon(self.icon_save),
                                    "&Save", self,
                                    shortcut=QKeySequence.Save,
                                    triggered=self.file_save)
        tb.addAction(self.action_save)
        menu.addAction(self.action_save)

        self.action_save_as = QAction(QIcon(self.icon_saveas),
                                        "Save &As...", self,
                                        shortcut=Qt.CTRL + Qt.SHIFT + Qt.Key_S,
                                        triggered=self.file_save_as)
        tb.addAction(self.action_save_as)
        menu.addAction(self.action_save_as)
        menu.addSeparator()

        self.action_print = QAction(QIcon(self.icon_print),
                                            "&Print", self, priority=QAction.LowPriority,
                                            shortcut=QKeySequence.Print,
                                            triggered=self.file_print)
        tb.addAction(self.action_print)
        menu.addAction(self.action_print)

        self.action_print_preview = QAction(QIcon(self.icon_print),
                                            "Print Preview", self,
                                            shortcut=Qt.CTRL + Qt.SHIFT + Qt.Key_P,
                                            triggered=self.file_print_preview)
        menu.addAction(self.action_print_preview)

        self.action_print_pdf = QAction(QIcon(self.icon_pdf),
                                        "&Export to PDF", self, priority=QAction.LowPriority,
                                        shortcut=Qt.CTRL + Qt.Key_D,
                                        triggered=self.file_print_pdf)
        tb.addAction(self.action_print_pdf)
        menu.addAction(self.action_print_pdf)

    def setup_edit_actions(self):
        tb = QToolBar(self)
        tb.setWindowTitle("Edit Actions")
        self.addToolBar(tb)

        menu = QMenu("&Edit", self)
        self.menuBar().addMenu(menu)

        self.action_undo = QAction(QIcon(self.icon_undo),
                                    "&Undo", self,
                                    shortcut=QKeySequence.Undo)
        tb.addAction(self.action_undo)
        menu.addAction(self.action_undo)

        self.action_redo = QAction(QIcon(self.icon_redo),
                                    "&Redo", self, priority=QAction.LowPriority,
                                    shortcut=QKeySequence.Redo)
        tb.addAction(self.action_redo)
        menu.addAction(self.action_redo)
        menu.addSeparator()

        self.action_cut = QAction(QIcon(self.icon_cut),
                                    "Cu&t", self, priority=QAction.LowPriority,
                                    shortcut=QKeySequence.Cut)
        tb.addAction(self.action_cut)
        menu.addAction(self.action_cut)

        self.action_copy = QAction(QIcon(self.icon_copy),
                                    "&Copy", self, priority=QAction.LowPriority,
                                    shortcut=QKeySequence.Copy)
        tb.addAction(self.action_copy)
        menu.addAction(self.action_copy)

        self.action_paste = QAction(QIcon(self.icon_paste),
                                    "&Paste", self, priority=QAction.LowPriority,
                                    shortcut=QKeySequence.Paste,
                                    enabled=(len(QApplication.clipboard().text()) != 0))
        tb.addAction(self.action_paste)
        menu.addAction(self.action_paste)

    def setup_text_actions(self):
        tb = QToolBar(self)
        tb.setWindowTitle("Format Actions")
        self.addToolBar(tb)

        menu = QMenu("F&ormat", self)
        self.menuBar().addMenu(menu)

        self.action_text_bold = QAction(QIcon(self.icon_bold),
                                        "&Bold", self, priority=QAction.LowPriority,
                                        shortcut=Qt.CTRL + Qt.Key_B,
                                        triggered=self.text_bold, checkable=True)
        bold = QFont()
        bold.setBold(True)
        self.action_text_bold.setFont(bold)
        tb.addAction(self.action_text_bold)
        menu.addAction(self.action_text_bold)

        self.action_text_italic = QAction(QIcon(self.icon_italic),
                                            "&Italic", self, priority=QAction.LowPriority,
                                            shortcut=Qt.CTRL + Qt.Key_I,
                                            triggered=self.text_italic, checkable=True)
        italic = QFont()
        italic.setItalic(True)
        self.action_text_italic.setFont(italic)
        tb.addAction(self.action_text_italic)
        menu.addAction(self.action_text_italic)

        self.action_text_underline = QAction(QIcon(self.icon_underline),
                                                "&Underline", self, priority=QAction.LowPriority,
                                                shortcut=Qt.CTRL + Qt.Key_U,
                                                triggered=self.text_underline, checkable=True)
        underline = QFont()
        underline.setUnderline(True)
        self.action_text_underline.setFont(underline)
        tb.addAction(self.action_text_underline)
        menu.addAction(self.action_text_underline)

        menu.addSeparator()

        grp = QActionGroup(self, triggered=self.text_align)

        # Make sure the alignLeft is always left of the alignRight.
        self.action_align_left = QAction(QIcon(self.icon_left), "&Left", grp)
        self.action_align_center = QAction(QIcon(self.icon_center), "C&enter", grp)
        self.action_align_right = QAction(QIcon(self.icon_right), "&Right", grp)
        self.action_align_justify = QAction(QIcon(self.icon_just), "&Justify", grp)

        self.action_align_left.setShortcut(Qt.CTRL + Qt.Key_L)
        self.action_align_left.setCheckable(True)
        self.action_align_left.setPriority(QAction.LowPriority)

        self.action_align_center.setShortcut(Qt.CTRL + Qt.Key_E)
        self.action_align_center.setCheckable(True)
        self.action_align_center.setPriority(QAction.LowPriority)

        self.action_align_right.setShortcut(Qt.CTRL + Qt.Key_R)
        self.action_align_right.setCheckable(True)
        self.action_align_right.setPriority(QAction.LowPriority)

        self.action_align_justify.setShortcut(Qt.CTRL + Qt.Key_J)
        self.action_align_justify.setCheckable(True)
        self.action_align_justify.setPriority(QAction.LowPriority)

        tb.addActions(grp.actions())
        menu.addActions(grp.actions())
        menu.addSeparator()

        pix = QPixmap(16, 16)
        pix.fill(Qt.black)
        self.action_text_color = QAction(QIcon(pix),
                                            "&Color...", self, triggered=self.text_color)
        tb.addAction(self.action_text_color)
        menu.addAction(self.action_text_color)

    def setup_other_actions(self):
        tb = QToolBar(self)
        tb.setWindowTitle("Other Actions")
        self.addToolBar(tb)

        menu = QMenu("&About", self)
        self.menuBar().addMenu(menu)

        self.action_about = QAction(QIcon(self.icon_about),
                                    "About &" + self.win_title, self,
                                    shortcut=QKeySequence.HelpContents,
                                    triggered=self.parent.action_about_triggered)
        tb.addAction(self.action_about)
        menu.addAction(self.action_about)
        menu.addAction(QIcon(self.icon_qt), "About &Qt", qApp.aboutQt)

        self.action_quit = QAction(QIcon(self.icon_quit),
                                    "&Quit", self,
                                    shortcut=QKeySequence.Quit,
                                    triggered=self.close)
        menu.addAction(self.action_quit)
        tb.addAction(self.action_quit)

    def setup_style_actions(self):
        tb = QToolBar(self)
        tb.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        tb.setWindowTitle("Format Actions")
        self.addToolBarBreak(Qt.TopToolBarArea)
        self.addToolBar(tb)

        combo_style = QComboBox(tb)
        tb.addWidget(combo_style)
        combo_style.addItem("Standard")
        combo_style.addItem("Bullet List (Disc)")
        combo_style.addItem("Bullet List (Circle)")
        combo_style.addItem("Bullet List (Square)")
        combo_style.addItem("Ordered List (Decimal)")
        combo_style.addItem("Ordered List (Alpha lower)")
        combo_style.addItem("Ordered List (Alpha upper)")
        combo_style.addItem("Ordered List (Roman lower)")
        combo_style.addItem("Ordered List (Roman upper)")
        combo_style.activated.connect(self.text_style)

        self.combo_font = QFontComboBox(tb)
        tb.addWidget(self.combo_font)
        self.combo_font.activated[str].connect(self.text_family)
        self.combo_size = QComboBox(tb)
        self.combo_size.setObjectName("combo_size")
        tb.addWidget(self.combo_size)
        self.combo_size.setEditable(True)

        db = QFontDatabase()
        for size in db.standardSizes():
            self.combo_size.addItem("%s" % (size))
        self.combo_size.activated[str].connect(self.text_size)
        self.combo_size.setCurrentIndex(self.combo_size.findText("%s" % (QApplication.font().pointSize())))

    def load(self, f):
        if not QFile.exists(f):
            return False
        fh = QFile(f)
        if not fh.open(QFile.ReadOnly):
            return False
        data = fh.readAll()
        codec = QTextCodec.codecForHtml(data)
        unistr = codec.toUnicode(data)
        if Qt.mightBeRichText(unistr):
            self.text_edit.setHtml(unistr)
        else:
            self.text_edit.setPlainText(unistr)
        self.set_current_filename(f)
        return True

    def maybe_save(self):
        if not self.text_edit.document().isModified():
            return True

        if self.file_name.startswith(':/'):
            return True

        ret = QMessageBox.warning(self, "Document Modified" + self.win_title,
                                    "The document has been modified.\n"
                                    "Do you want to save your changes?",
                                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        if ret == QMessageBox.Save:
            return self.file_save()
        if ret == QMessageBox.Cancel:
            return False
        return True

    def set_current_filename(self, file_name = ''):
        self.file_name = file_name
        self.text_edit.document().setModified(False)
        if not file_name:
            shown_name = 'untitled.txt'
        else:
            shown_name = QFileInfo(file_name).fileName()
        self.setWindowTitle(self.tr("%s[*] - %s" % (shown_name, self.win_title)))
        self.setWindowModified(False)

    def file_open(self):
        fn = QFileDialog.getOpenFileName(self, "Open File... - " + self.win_title, self.save_path,
                                            "HTML-Files (*.htm *.html);;All Files (*)")
        if fn:
            fn_info = QFileInfo(fn)
            fn_dir = fn_info.absolutePath()
            self.save_path = fn_dir
            self.load(fn)

    def file_save(self):
        if not self.file_name:
            return self.file_save_as()
        writer = QTextDocumentWriter(self.file_name)
        success = writer.write(self.text_edit.document())
        if success:
            self.text_edit.document().setModified(False)
        return success

    def file_save_as(self):
        fn = QFileDialog.getSaveFileName(self, "Save as... - " + self.win_title, self.save_path,
                                            "HTML Files (*.html *.htm);;Text Files (*.txt);;ODF files (*.odt);;All Files (*)")

        if not fn:
            return False

        lfn = fn.lower()
        if not (lfn.endswith('.htm') or lfn.endswith('.html') or lfn.endswith('.odt') or lfn.endswith('.txt')):
            # The default.
            fn += '.html'

        self.set_current_filename(fn)
        fn_info = QFileInfo(fn)
        fn_dir = fn_info.absolutePath()
        self.save_path = fn_dir
        return self.file_save()

    def file_print(self):
        printer = QPrinter(QPrinter.HighResolution)
        dlg = QPrintDialog(printer, self)
        if self.text_edit.textCursor().hasSelection():
            dlg.addEnabledOption(QAbstractPrintDialog.PrintSelection)
        dlg.setWindowTitle("Print Document - " + self.win_title)
        if dlg.exec_() == QDialog.Accepted:
            self.text_edit.print_(printer)
        del dlg

    def file_print_preview(self):
        printer = QPrinter(QPrinter.HighResolution)
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(self.print_preview)
        preview.exec_()

    def print_preview(self, printer):
        self.text_edit.print_(printer)

    def file_print_pdf(self):
        fn = QFileDialog.getSaveFileName(self, "Export to PDF - " + self.win_title, self.save_path,
                                            "PDF files (*.pdf)")
        fn_info = QFileInfo(fn)
        if fn:
            if fn_info.suffix() == "":
                fn += '.pdf'
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(fn)
            self.text_edit.document().print_(printer)

        fn_dir = fn_info.absolutePath()
        self.save_path = fn_dir

    def text_bold(self):
        fmt = QTextCharFormat()
        fmt.setFontWeight(self.action_text_bold.isChecked() and QFont.Bold or QFont.Normal)
        self.merge_format_on_word_or_selection(fmt)

    def text_underline(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(self.action_text_underline.isChecked())
        self.merge_format_on_word_or_selection(fmt)

    def text_italic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(self.action_text_italic.isChecked())
        self.merge_format_on_word_or_selection(fmt)

    def text_family(self, family):
        fmt = QTextCharFormat()
        fmt.setFontFamily(family)
        self.merge_format_on_word_or_selection(fmt)

    def text_size(self, point_size):
        point_size = float(point_size)
        if point_size > 0:
            fmt = QTextCharFormat()
            fmt.setFontPointSize(point_size)
            self.merge_format_on_word_or_selection(fmt)

    def text_style(self, style_index):
        cursor = self.text_edit.textCursor()
        if style_index:
            style_dict = {
                1: QTextListFormat.ListDisc,
                2: QTextListFormat.ListCircle,
                3: QTextListFormat.ListSquare,
                4: QTextListFormat.ListDecimal,
                5: QTextListFormat.ListLowerAlpha,
                6: QTextListFormat.ListUpperAlpha,
                7: QTextListFormat.ListLowerRoman,
                8: QTextListFormat.ListUpperRoman,
            }
            style = style_dict.get(style_index, QTextListFormat.ListDisc)
            cursor.beginEditBlock()
            block_fmt = cursor.blockFormat()
            list_fmt = QTextListFormat()
            if cursor.currentList():
                list_fmt = cursor.currentList().format()
            else:
                list_fmt.setIndent(block_fmt.indent() + 1)
                block_fmt.setIndent(0)
                cursor.setBlockFormat(block_fmt)
            list_fmt.setStyle(style)
            cursor.createList(list_fmt)
            cursor.endEditBlock()
        else:
            bfmt = QTextBlockFormat()
            bfmt.setObjectIndex(-1)
            cursor.mergeBlockFormat(bfmt)

    def text_color(self):
        col = QColorDialog.getColor(self.text_edit.textColor(), self)
        if not col.isValid():
            return
        fmt = QTextCharFormat()
        fmt.setForeground(col)
        self.merge_format_on_word_or_selection(fmt)
        self.color_changed(col)

    def text_align(self, action):
        if action == self.action_align_left:
            self.text_edit.setAlignment(Qt.AlignLeft | Qt.AlignAbsolute)
        elif action == self.action_align_center:
            self.text_edit.setAlignment(Qt.AlignHCenter)
        elif action == self.action_align_right:
            self.text_edit.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)
        elif action == self.action_align_justify:
            self.text_edit.setAlignment(Qt.AlignJustify)

    def current_char_format_changed(self, format):
        self.font_changed(format.font())
        self.color_changed(format.foreground().color())

    def cursor_position_changed(self):
        self.alignment_changed(self.text_edit.alignment())

    def clipboard_data_changed(self):
        self.action_paste.setEnabled(len(QApplication.clipboard().text()) != 0)

    def merge_format_on_word_or_selection(self, format):
        cursor = self.text_edit.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
        cursor.mergeCharFormat(format)
        self.text_edit.mergeCurrentCharFormat(format)

    def font_changed(self, font):
        self.combo_font.setCurrentIndex(self.combo_font.findText(QFontInfo(font).family()))
        self.combo_size.setCurrentIndex(self.combo_size.findText("%s" % font.pointSize()))
        self.action_text_bold.setChecked(font.bold())
        self.action_text_italic.setChecked(font.italic())
        self.action_text_underline.setChecked(font.underline())

    def color_changed(self, color):
        pix = QPixmap(16, 16)
        pix.fill(color)
        self.action_text_color.setIcon(QIcon(pix))

    def alignment_changed(self, alignment):
        if alignment and Qt.AlignLeft:
            self.action_align_left.setChecked(True)
        elif alignment and Qt.AlignHCenter:
            self.action_align_center.setChecked(True)
        elif alignment and Qt.AlignRight:
            self.action_align_right.setChecked(True)
        elif alignment and Qt.AlignJustify:
            self.action_align_justify.setChecked(True)
