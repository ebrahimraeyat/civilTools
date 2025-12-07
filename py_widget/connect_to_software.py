from pathlib import Path

from PySide2 import QtWidgets, QtGui, QtCore
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QMessageBox

import FreeCADGui as Gui
import FreeCAD

import find_and_register_softwares as far


civiltools_path = Path(__file__).parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'connect_to_software.ui'))
        self.require_restart = False
        self.title = ''
        self.selected_software = None
        self.software_buttons = []  # Track buttons for cleanup
        self.create_connections()

    def create_connections(self):
        self.form.find_button.clicked.connect(self.show)
        self.form.connect_button.clicked.connect(self.connect_selected_software)

    def clear_layout(self):
        """Remove all buttons from the layout"""
        # Get the layout from the widget
        layout = self.form.softwares_layout.layout()
        if layout is None:
            return
        
        # Disconnect and remove all buttons
        for button in self.software_buttons:
            try:
                button.clicked.disconnect()
            except:
                pass
            layout.removeWidget(button)
            button.deleteLater()
        self.software_buttons.clear()
        self.selected_software = None

    def show(self):
        """Add software windows to the dialog"""
        # Clear previous buttons
        self.clear_layout()

        # Get the layout from the widget
        layout = self.form.softwares_layout.layout()
        if layout is None:
            # If no layout exists, create one
            layout = QtWidgets.QVBoxLayout()
            self.form.softwares_layout.setLayout(layout)
        
        # Get executable paths of supported software
        software_name = self.get_software_name()
        softwares = far.get_softwares_process([software_name])
        if not softwares:
            QMessageBox.warning(None, "No Software Found", "No supported software is running.")
            return

        # Capture and minimize all windows
        all_windows = []
        for software in softwares:
            try:
                window = software.get_screen_shot()
                all_windows.append(window)
            except Exception as e:
                print(f"Error capturing window for {software.exe_path}: {e}")
        
        for window in all_windows:
            window.minimize()

        # Create buttons for each software
        for software in softwares:
            button = QtWidgets.QPushButton(self)
            
            # Load and scale the screenshot
            pixmap = QtGui.QPixmap(str(software.screenshot_path))
            pixmap = pixmap.scaled(150, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Create icon and set button properties
            icon = QtGui.QIcon(pixmap)
            button.setIcon(icon)
            button.setIconSize(QtCore.QSize(150, 100))
            
            text = software.exe_path.parent.name
            button.setText(f"{text}")
            button.setStyleSheet("text-align: center; margin: 5px;")
            button.setFixedSize(300, 150)
            button.setCheckable(True)
            
            # Connect button click to selection handler
            button.clicked.connect(lambda s=software, b=button: self.select_software(s, b))
            
            # Add button to layout
            layout.addWidget(button)
            self.software_buttons.append(button)
        
        # Add stretch at the end to keep buttons at top
        layout.addStretch()
        
        # Set window flags
        if hasattr(self, "setWindowFlags"):
            self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

    def select_software(self, software, button):
        """Handle software selection"""
        # Uncheck previously selected button
        for btn in self.software_buttons:
            if btn != button:
                btn.setChecked(False)
        
        # Store selected software
        self.selected_software = software
        button.setChecked(True)
        print(f"Selected: {software.title}")

    def connect_selected_software(self):
        """Connect to the selected software and save the path"""
        if self.selected_software is None:
            QMessageBox.warning(None, "No Selection", "Please select a software window first.")
            return
        
        software = self.selected_software
        
        # Restore default window behavior
        self.title = software.title
        self.setWindowFlags(QtCore.Qt.Widget)
        try:
            ret = far.connect_to_software(software)
            if isinstance(ret, str):
                param = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/civilTools")
                param.SetString("pid_moniker", ret)
                param.SetString("last_exe_path_software", str(software.exe_path))
                QMessageBox.information(self,
                                    "Connected",
                                    f"Connected to {software}.")
            if ret is True:
                QMessageBox.information(self,
                                    "Connected",
                                    f"Connected to {software}."
                                    "\nFreeCAD restarts automatically to apply the changes.")
                self.require_restart = True
            self.form.close()
        except Exception as e:
            QMessageBox.critical(self, "Connection Failed", f"Failed to connect to {software.exe_path}.\n{e}")

    def get_software_name(self):
        if self.form.etabs_radiobutton.isChecked():
            return "ETABS"
        elif self.form.sap2000_radiobutton.isChecked():
            return "SAP2000"
        elif self.form.safe_radiobutton.isChecked():
            return "SAFE"