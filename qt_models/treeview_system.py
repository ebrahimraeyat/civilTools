"""
Reworked code based on
http://trevorius.com/scrapbook/uncategorized/pyqt-custom-abstractitemmodel/

Adapted to Qt5 and fixed column/row bug.

TODO: handle changing data.
"""

import sys
import csv
from pathlib import Path

# from PyQt5 import QtCore, QtWidgets
# from PyQt5.QtCore import Qt
from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import Qt


class CustomNode(object):
    def __init__(self, data):
        self._data = data
        if type(data) == tuple:
            self._data = list(data)
        if type(data) is str or not hasattr(data, '__getitem__'):
            self._data = [data]

        self._columncount = len(self._data)
        self._children = []
        self._parent = None
        self._row = 0

    def data(self, column):
        if column >= 0 and column < len(self._data):
            return self._data[column]

    def columnCount(self):
        return self._columncount

    def childCount(self):
        return len(self._children)

    def child(self, row):
        if row >= 0 and row < self.childCount():
            return self._children[row]

    def parent(self):
        return self._parent

    def row(self):
        return self._row

    def addChild(self, child):
        child._parent = self
        child._row = len(self._children)
        self._children.append(child)
        self._columncount = max(child.columnCount(), self._columncount)


class CustomModel(QtCore.QAbstractItemModel):
    def __init__(self, nodes, headers):
        QtCore.QAbstractItemModel.__init__(self)
        self._root = CustomNode(None)
        for node in nodes:
            self._root.addChild(node)
        self.headers = headers

    def rowCount(self, index):
        if index.isValid():
            return index.internalPointer().childCount()
        return self._root.childCount()

    def addChild(self, node, _parent):
        if not _parent or not _parent.isValid():
            parent = self._root
        else:
            parent = _parent.internalPointer()
        parent.addChild(node)

    def index(self, row, column, _parent=None):
        if not _parent or not _parent.isValid():
            parent = self._root
        else:
            parent = _parent.internalPointer()

        if not QtCore.QAbstractItemModel.hasIndex(self, row, column, _parent):
            return QtCore.QModelIndex()

        child = parent.child(row)
        if child:
            return QtCore.QAbstractItemModel.createIndex(self, row, column, child)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if index.isValid():
            p = index.internalPointer().parent()
            if p:
                return QtCore.QAbstractItemModel.createIndex(self, p.row(), 0, p)
        return QtCore.QModelIndex()

    def columnCount(self, index):
        if index.isValid():
            return index.internalPointer().columnCount()
        return self._root.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None
        column = index.column()
        node = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return node.data(index.column())
        elif role == Qt.TextAlignmentRole:
            if column == 0:
                return int(Qt.AlignLeft | Qt.AlignVCenter)
            return int(Qt.AlignHCenter | Qt.AlignVCenter)
        return None

    def headerData(self, section, orientation, role):
        if (orientation == Qt.Horizontal and
            role == Qt.DisplayRole):
            assert 0 <= section <= len(self.headers)
            return self.headers[section]
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return int(Qt.AlignHCenter | Qt.AlignVCenter)
            return int(Qt.AlignLeft | Qt.AlignVCenter)
        return

    # def asRecord(self, index):
    #     leaf = self.nodeFromIndex(index)
    #     if leaf is not None and isinstance(leaf, LeafNode):
    #         return leaf.asRecord()
    #     return []


class MyTree():
    """
    """
    def __init__(self):
        self.items = {}

        # Set some random data:
        dir_ = r'C:\Users\ebrahim\AppData\Roaming\FreeCAD\Mod\civilTools\db'
        csv_path = Path(dir_) / 'systems.csv'
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                # print(row)
                if (
                    row[0][1] in ['ا', 'ب', 'پ', 'ت', 'ث'] or
                    row[0][0] in ['ا', 'ب', 'پ', 'ت', 'ث']
                    ):
                    i = row[0]
                    # root = self.items.get(i, None)
                    # if root is None:
                    root = CustomNode(i)
                    self.items[i] = root
                    if row[0][0] not in 'FH':
                        continue

                root.addChild(CustomNode(row))

        self.tw = QtWidgets.QTreeView()
        headers=('System', 'Ru', 'Omega', 'Cd', 'H_max', 'alpha', 'beta', 'note', 'ID')
        self.tw.setModel(CustomModel(list(self.items.values()), headers=headers))
        self.tw.clicked.connect(self.update_model)

    def update_model(self):
        self.get_treewidget_item_text(self.tw)

    def get_treewidget_item_text(self, widget):
        indexes = widget.selectedIndexes()

        print(len(indexes))
        index = indexes[0]
        if index.isValid():
            data = index.internalPointer()._data
            if len(data) == 1:
                return
            lateral = data[0]
            lateral = lateral.split('-')[1]
            lateral = lateral.lstrip(' ')
            system = index.parent().data()
            system = system.split('-')[1]
            system = system.lstrip(' ')
            return system, lateral


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mytree = MyTree()
    mytree.tw.show()
    sys.exit(app.exec_())