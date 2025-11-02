from PySide6.QtCore import QUrl, Qt, QSettings, QDir
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QFileDialog, QPushButton, QMenu, QTreeView, QSplitter, QLabel, QSizePolicy
from PySide6.QtGui import QAction, QStandardItemModel, QStandardItem, QIcon
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage
import os

class PDFFileSystemModel(QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHorizontalHeaderLabels(["PDF Files and Folders"])
        self.root_path = os.path.dirname(os.path.abspath(__file__))
        self.current_path = self.root_path
        self.populate_model(self.invisibleRootItem(), self.current_path)
        
    def populate_model(self, parent_item, directory_path):
        parent_item.removeRows(0, parent_item.rowCount())
        directory = QDir(directory_path)
        up_item = QStandardItem("")
        up_item.setData(os.path.dirname(directory_path), Qt.UserRole)
        up_item.setIcon(QIcon.fromTheme("go-up"))
        parent_item.appendRow(up_item)
        directories = directory.entryInfoList(QDir.Filter.Dirs | QDir.Filter.NoDotAndDotDot, QDir.SortFlag.Name)
        for dir_info in directories:
            dir_item = QStandardItem(dir_info.fileName())
            dir_item.setData(dir_info.filePath(), Qt.UserRole)
            dir_item.setIcon(QIcon.fromTheme("folder"))
            parent_item.appendRow(dir_item)
            placeholder = QStandardItem("Loading...")
            dir_item.appendRow(placeholder)
        pdf_files = directory.entryInfoList(["*.pdf"], QDir.Filter.Files, QDir.SortFlag.Name)
        for file_info in pdf_files:
            file_item = QStandardItem(file_info.fileName())
            file_item.setData(file_info.filePath(), Qt.UserRole)
            file_item.setIcon(QIcon.fromTheme("application-pdf"))
            parent_item.appendRow(file_item)
    
    def navigate_to(self, path):
        self.current_path = path
        self.populate_model(self.invisibleRootItem(), path)

class SearchLineEdit(QLineEdit):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() == Qt.Key_Return:
            self.main_window.search_text(self.text())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Viewer")
        self.setGeometry(0, 28, 1000, 750)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.tree_model = PDFFileSystemModel()
        self.path_label = QLabel()
        self.path_label.setText(self.tree_model.current_path)
        self.path_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.main_layout.addWidget(self.path_label)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter)
        self.nav_widget = QWidget()
        self.nav_layout = QVBoxLayout(self.nav_widget)
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.tree_model)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.clicked.connect(self.on_tree_clicked)
        self.tree_view.expanded.connect(self.on_tree_expanded)
        self.nav_layout.addWidget(self.tree_view)
        self.splitter.addWidget(self.nav_widget)
        self.pdf_widget = QWidget()
        self.pdf_layout = QVBoxLayout(self.pdf_widget)
        self.webView = QWebEngineView()
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PluginsEnabled, True)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PdfViewerEnabled, True)
        self.pdf_layout.addWidget(self.webView)
        self.search_input = SearchLineEdit(self)
        self.search_input.setPlaceholderText("Enter text to search...")
        self.pdf_layout.addWidget(self.search_input)
        self.splitter.addWidget(self.pdf_widget)
        self.splitter.setSizes([250, 750])
        self.settings = QSettings("MyCompany", "PDFViewer")
        self.recent_files = self.settings.value("recentFiles", [])
        self.create_file_menu()
    
    def on_tree_clicked(self, index):
        item = self.tree_model.itemFromIndex(index)
        file_path = item.data(Qt.UserRole)
        if item.text() == "":
            self.tree_model.navigate_to(file_path)
            self.path_label.setText(file_path)
            return
        if os.path.isdir(file_path):
            self.tree_model.navigate_to(file_path)
            self.path_label.setText(file_path)
            return
        if file_path and file_path.lower().endswith('.pdf'):
            self.path_label.setText(file_path)
            pdf_url = QUrl.fromLocalFile(file_path)
            pdf_url.setFragment("zoom=page-width")
            self.webView.setUrl(pdf_url)
    
    def on_tree_expanded(self, index):
        item = self.tree_model.itemFromIndex(index)
        file_path = item.data(Qt.UserRole)
        if item.rowCount() == 1 and item.child(0).text() == "Loading...":
            item.removeRow(0)
            self.tree_model.populate_model(item, file_path)
    
    def create_file_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        open_action = QAction('Open', self)
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)
        self.recent_menu = QMenu('Recent Files', self)
        file_menu.addMenu(self.recent_menu)
        self.update_recent_files_menu()
    
    def update_recent_files_menu(self):
        self.recent_menu.clear()
        for file in self.recent_files:
            action = QAction(os.path.basename(file), self)
            action.setData(file)
            action.triggered.connect(self.open_recent_file)
            self.recent_menu.addAction(action)
    
    def open_file_dialog(self):
        file_dialog = QFileDialog()
        filename, _ = file_dialog.getOpenFileName(self, "Open File", "", "All Files (*)")
        if filename:
            self.load_file(filename)
    
    def load_file(self, filename):
        self.webView.setUrl(QUrl("file:///" + filename.replace('\\', '/')))
        self.add_to_recent_files(filename)
    
    def add_to_recent_files(self, filename):
        if filename in self.recent_files:
            self.recent_files.remove(filename)
        self.recent_files.insert(0, filename)
        self.recent_files = self.recent_files[:5]
        self.settings.setValue("recentFiles", self.recent_files)
        self.update_recent_files_menu()
    
    def open_recent_file(self):
        action = self.sender()
        if action:
            self.load_file(action.data())
    
    def search_text(self, text):
        flag = QWebEnginePage.FindFlag.FindCaseSensitively
        if text:
            self.webView.page().findText(text, flag)
        else:
            self.webView.page().stopFinding()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())