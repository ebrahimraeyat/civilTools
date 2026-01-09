from pathlib import Path

from PySide.QtGui import QMessageBox, QPixmap, QImage
from PySide.QtCore import Qt

from PySide.QtGui import QApplication

import tempfile
import os

import FreeCADGui as Gui

from functions.list_autocad_printers import list_autocad_plot_devices, list_windows_printers, get_autocad_plot_resources, get_printer_media_names
from functions.dwg_to_pdf import DwgToPdf

try:
    from pdf2image import convert_from_path
except ImportError:
    package = 'pdf2image'
    from freecad_funcs import install_package
    install_package(package_name=package)
    from pdf2image import convert_from_path


civiltools_path = Path(__file__).parent.parent.parent


class Form:
    
    def __init__(self):
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'import_export' / 'export_dwg_to_pdf.ui'))
        self.selected_blocks = []  # Store selected blocks
        self.preview_pdf = None  # Store temporary preview file
        self.pdf_viewer = None
        self.setup_pdf_viewer()
        self.fill_printers()
        self.fill_paper_sizes()
        self.fill_styles()
        self.create_connections()
        self.dwg_to_pdf = DwgToPdf()
        # self.fill_block_names()
        # self.fill_drawing_names()

    def fill_drawing_names(self):
        drawing_names = self.dwg_to_pdf.get_all_open_drawing_names()
        self.form.drawing_names.addItems(drawing_names)
        if self.dwg_to_pdf.dwg_name in drawing_names:
            i = self.form.drawing_names.findText (self.dwg_to_pdf.dwg_name)
            self.form.drawing_names.setCurrentIndex(i)
            

    def fill_block_names(self):
        blocks = self.dwg_to_pdf.get_all_block_definitions()
        self.form.block_names.addItems(blocks)


    def setup_pdf_viewer(self):
        """Setup PDF viewer widget"""
        try:
            from PySide2.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
            from PySide2.QtCore import QUrl
            
            # Create custom profile with PDF viewer enabled
            profile = QWebEngineProfile("PDF")
            profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
            
            # Create page with custom profile
            page = QWebEnginePage(profile)
            
            self.pdf_viewer = QWebEngineView()
            self.pdf_viewer.setPage(page)
            
            # Enable PDF viewing
            settings = self.pdf_viewer.settings()
            settings.setAttribute(QWebEngineProfile.PluginsEnabled, True)
            
            # Replace preview label with PDF viewer
            self.form.preview_label.hide()
            layout = self.form.preview_label.parent().layout()
            layout.replaceWidget(self.form.preview_label, self.pdf_viewer)
            self.pdf_viewer.setMinimumSize(400, 300)
            
        except Exception as e:
            print(f"WebEngine setup error: {e}")
            self.pdf_viewer = None

    def fill_printers(self):
        devices = list_autocad_plot_devices()
        win_printers = list_windows_printers()
        pdf_printers = [printer for printer in devices + win_printers if 'pdf' in printer.lower()]
        self.form.printers.clear()
        self.form.printers.addItems(pdf_printers)
        default_printer = "DWG To PDF.pc3"
        if default_printer in pdf_printers:
            self.form.printers.setCurrentText(default_printer)
    
    def fill_styles(self):
        styles = get_autocad_plot_resources()
        self.form.plot_style.clear()
        self.form.plot_style.addItems(styles)
        default_style = "monochrome.ctb"
        if default_style in styles:
            self.form.plot_style.setCurrentText(default_style)


    def fill_filename(self):
        try:
            name = self.etabs.get_filename().with_suffix('.dxf')
        except:
            name = ''
        self.form.filename.setText(str(name))

    def create_connections(self):
        # self.form.browse.clicked.connect(self.browse)
        self.form.select_blocks_button.clicked.connect(self.select_blocks)
        self.form.export_button.clicked.connect(self.export)  # Separate export button
        self.form.cancel_pushbutton.clicked.connect(self.reject)
        self.form.printers.currentIndexChanged.connect(self.fill_paper_sizes)
        self.form.drawing_names.currentIndexChanged.connect(self.on_change_drawing_name)
        self.form.auto_numbering.clicked.connect(self.set_auto_numbering)
        # self.form.paper_size_combobox.currentIndexChanged.connect(self.create_preview)
        # self.form.plot_style.currentIndexChanged.connect(self.create_preview)

    def set_auto_numbering(self):
        no_blocks = self.dwg_to_pdf.add_and_number_attributes(*self.get_selected_layout())
        QMessageBox.information(None, "Auto Numbering", f"{no_blocks} Sheets get numbered in {self.dwg_to_pdf.dwg_name} drawing.")

    def on_change_drawing_name(self):
        drawing_name = self.form.drawing_names.currentText()
        self.dwg_to_pdf.get_doc_according_to_drawing_name(drawing_name)
        self.selected_blocks = []
        self.form.select_blocks_button.setText("Select Blocks")


    def fill_paper_sizes(self):
        device = self.form.printers.currentText()
        self.form.paper_size_combobox.clear()
        paper_sizes = get_printer_media_names(device)
        self.form.paper_size_combobox.addItems(paper_sizes)

    def get_selected_layout(self):
        if self.form.left_up_vertical.isChecked():
            checked_button = self.form.left_up_vertical
        if self.form.right_up_vertical.isChecked():
            checked_button = self.form.right_up_vertical
        if self.form.left_down_vertical.isChecked():
            checked_button = self.form.left_down_vertical
        if self.form.right_down_vertical.isChecked():
            checked_button = self.form.right_down_vertical
        if self.form.left_up_horizontal.isChecked():
            checked_button = self.form.left_up_horizontal
        if self.form.right_up_horizontal.isChecked():
            checked_button = self.form.right_up_horizontal
        if self.form.left_down_horizontal.isChecked():
            checked_button = self.form.left_down_horizontal
        if self.form.right_down_horizontal.isChecked():
            checked_button = self.form.right_down_horizontal
        horizontal, vertical, prefer_dir = checked_button.objectName().split("_")
        return horizontal, vertical, prefer_dir

    # def browse(self):
    #     ext = '.dxf'
    #     from PySide.QtGui import QFileDialog
    #     filters = f"{ext[1:]} (*{ext})"
    #     filename, _ = QFileDialog.getSaveFileName(None, 'select file',
    #                                             None, filters)
    #     if not filename:
    #         return
    #     if not filename.lower().endswith(ext):
    #         filename += ext
    #     self.form.filename.setText(filename)

    def select_blocks(self):
        if self.form.select_block_by_name.isChecked():
            block_name = self.form.block_names.currentText()
            self.selected_blocks = self.dwg_to_pdf.select_block_by_name(block_name)
        else:
            """Select blocks and show preview of first block"""
            self.selected_blocks = self.dwg_to_pdf.get_selected_blocks()
        if len(self.selected_blocks) == 0:
            self.form.preview_label.clear()
            self.form.select_blocks_button.setText("Select Blocks")
            QMessageBox.warning(None, 'Selection', 'Please select some blocks in AutoCAD File.')
        else:
            # Create preview of first block
            self.create_preview(self.selected_blocks[0])
            self.form.select_blocks_button.setText(f"{len(self.selected_blocks)} blocks selected")
            self.form.auto_numbering.setEnabled(True)
            self.form.export_button.setEnabled(True)
            
    def create_preview(self, block_id=None):
        """Create preview image of the first selected block"""
        try:
            # Clear previous preview
            if self.preview_pdf and os.path.exists(self.preview_pdf):
                try:
                    os.remove(self.preview_pdf)
                    self.preview_pdf = None
                except:
                    pass

            if block_id is None and self.selected_blocks:
                block_id = self.selected_blocks[0]
            
            if not block_id:
                return

            # Create temporary PDF with unique name
            temp_dir = tempfile.gettempdir()
            import uuid
            unique_name = f"preview_{uuid.uuid4().hex[:8]}.pdf"
            self.preview_pdf = os.path.join(temp_dir, unique_name)
            
            # Plot block to PDF
            try:
                way = int(self.form.way_combobox.currentText())
                self.dwg_to_pdf.doc.SetVariable('FILEDIA', 0)
                self.dwg_to_pdf.plot_block_to_pdf(
                    block_id,
                    self.preview_pdf,
                    config_name=self.form.printers.currentText(),
                    stylesheet=self.form.plot_style.currentText(),
                    paper_size=self.form.paper_size_combobox.currentText(),
                    orientation=self.form.orientation_combobox.currentText(),
                    way=way,
                )
            except Exception as e:
                print(f"Plot error: {e}")
                return
            finally:
                try:
                    self.dwg_to_pdf.doc.SetVariable('FILEDIA', 1)
                except Exception:
                    pass

            # Wait for file to exist and have size > 0
            import time
            timeout = 3  # seconds
            start_time = time.time()
            while not os.path.exists(self.preview_pdf) or os.path.getsize(self.preview_pdf) == 0:
                if time.time() - start_time > timeout:
                    print("Timeout waiting for PDF creation")
                    return
                time.sleep(0.1)

            try:
                # Convert PDF to image
                images = convert_from_path(self.preview_pdf)
                if images:
                    img = images[0]
                    img = img.convert('RGB')
                    
                    # Convert PIL image to QPixmap
                    data = img.tobytes('raw', 'RGB')
                    qimage = QImage(data, img.size[0], img.size[1], img.size[0] * 3, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(qimage)
                    
                    # Scale to fit
                    # pixmap = pixmap.scaled(
                    #     self.form.preview_label.width(),
                    #     self.form.preview_label.height(),
                    #     Qt.KeepAspectRatio,
                    #     Qt.SmoothTransformation
                    # )
                    # Scale to fit label; because we rendered at high DPI the result will be crisp.


                    if QApplication is not None:
                        screen = QApplication.primaryScreen()
                        if screen:
                            geom = screen.availableGeometry()
                            screen_w, screen_h = geom.width(), geom.height()
                        else:
                            screen_w, screen_h = 1366, 768
                    else:
                        screen_w, screen_h = 1366, 768

                    # compute requested size from screen ratio
                    ratio = getattr(self, "preview_ratio", 0.6)
                    target_w = int(screen_w * ratio)
                    target_h = int(screen_h * ratio)

                    # Never exceed the label size (so layout remains clean)
                    label_w = max(1, self.form.preview_label.width())
                    label_h = max(1, self.form.preview_label.height())
                    target_w = min(target_w, label_w)
                    target_h = min(target_h, label_h)

                    pixmap = pixmap.scaled(target_w, target_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.form.preview_label.setPixmap(pixmap)
            except Exception as e:
                print(f"Image preview error: {e}")
        except Exception as e:
            print(f"Preview creation error: {e}")

    def export(self):
        """Export selected blocks to PDF"""
        if not self.selected_blocks:
            QMessageBox.warning(None, 'Selection', 'Please select some blocks in AutoCAD File.')
            return
        # ...existing export code using self.selected_blocks...
        horizontal, vertical, prefer_dir = self.get_selected_layout()
        way = int(self.form.way_combobox.currentText())
        printer = self.form.printers.currentText()
        style = self.form.plot_style.currentText()
        paper_size = self.form.paper_size_combobox.currentText()
        remove_pdf = self.form.remove_pdf_checkbox.isChecked()
        orientation = self.form.orientation_combobox.currentText()
        
        filename = self.dwg_to_pdf.export_dwg_to_pdf(
            horizontal,
            vertical,
            prefer_dir=prefer_dir,
            remove_pdfs=remove_pdf,
            way=way,
            config_name=printer,
            stylesheet=style,
            paper_size=paper_size,
            blocks_id=self.selected_blocks,  # Pass selected blocks,
            orientation=orientation,
        )

        if filename:
            from civiltools_python_functions import open_file
            open_file(filename)

    def getStandardButtons(self):
        return 0
    
    def reject(self):
        self.form.reject()

    # def __del__(self):
    #     """Cleanup temporary files"""
    #     if self.preview_pdf and os.path.exists(self.preview_pdf):
    #         try:
    #             os.remove(self.preview_pdf)
    #         except:
    #             pass
