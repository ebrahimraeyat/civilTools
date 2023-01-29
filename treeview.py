from pathlib import Path
import sys

from PyQt5 import QtCore, QtGui, QtWidgets

civiltools_path = Path(__file__).absolute()
sys.path.insert(0, civiltools_path)

from qt_models import treeview_system


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.centralwidget = QtWidgets.QWidget()
        self.treeView = QtWidgets.QTreeView(self.centralwidget)
        self.treeView.setGeometry(QtCore.QRect(220, 40, 291, 151))
        self.setCentralWidget(self.centralwidget)

    def set_system_treeview(self):
        items = {}

        # Set some random data:
        csv_path =  civiltools_path / 'db' / 'systems.csv'
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                if (
                    row[0][1] in ['ا', 'ب', 'پ', 'ت', 'ث'] or
                    row[0][0] in ['ا', 'ب', 'پ', 'ت', 'ث']
                    ):
                    i = row[0]
                    # root = items.get(i, None)
                    # if root is None:
                    root = treeview_system.CustomNode(i)
                    items[i] = root
                else:
                    root.addChild(treeview_system.CustomNode(row))
        headers = ('System', 'Ru', 'Omega', 'Cd', 'H_max', 'alpha', 'beta', 'note', 'ID')
        self.treeView.setModel(treeview_system.CustomModel(list(items.values()), headers=headers))


import sys
app = QtWidgets.QApplication(sys.argv)
ui = MainWindow()
ui.show()
sys.exit(app.exec_())