"""
Reworked code based on
http://trevorius.com/scrapbook/uncategorized/pyqt-custom-abstractitemmodel/

Adapted to Qt5 and fixed column/row bug.

TODO: handle changing data.
"""

import sys
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
        node = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return node.data(index.column())
        return None

    def headerData(self, section, orientation, role):
        if (orientation == Qt.Horizontal and
            role == Qt.DisplayRole):
            assert 0 <= section <= len(self.headers)
            return self.headers[section]
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
        for i in 'aba':
            root = self.items.get(i, None)
            if root is None:
                root = CustomNode(i)
                self.items[i] = root
            root.addChild(CustomNode(['d', 'e', 'f']))

        self.tw = QtWidgets.QTreeView()
        self.tw.setModel(CustomModel(list(self.items.values()), headers=('Load Case', 'SF')))

    def add_data(self, data):
        """
        TODO: how to insert data, and update tree.
        """
        # self.items[-1].addChild(CustomNode(['1', '2', '3']))
        # self.tw.setModel(CustomModel(self.items))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mytree = MyTree()
    mytree.tw.show()
    sys.exit(app.exec_())