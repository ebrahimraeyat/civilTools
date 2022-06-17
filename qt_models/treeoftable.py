
import bisect
from PySide2.QtCore import (QAbstractItemModel, QModelIndex, Qt)
# from PySide2.QtCore import Signal

KEY, NODE = range(2)


class BranchNode(object):

    def __init__(self, name, parent=None):
        super(BranchNode, self).__init__()
        self.name = name
        self.parent = parent
        self.children = []


    def orderKey(self):
        return self.name.lower()


    def toString(self):
        return self.name


    def __len__(self):
        return len(self.children)


    def childAtRow(self, row):
        assert 0 <= row < len(self.children)
        return self.children[row][NODE]
        

    def rowOfChild(self, child):
        for i, item in enumerate(self.children):
            if item[NODE] == child:
                return i
        return -1


    def childWithKey(self, key):
        if not self.children:
            return None
        for i in range(len(self.children)):
            if self.children[i][KEY] == key:
                return self.children[i][NODE]
        return None

    def insertChild(self, child):
        child.parent = self
        bisect.insort(self.children, (child.orderKey(), child))


    def hasLeaves(self):
        if not self.children:
            return False
        return isinstance(self.children[0], LeafNode)


class LeafNode(object):

    def __init__(self, fields, parent=None):
        super(LeafNode, self).__init__()
        self.parent = parent
        self.fields = fields


    def orderKey(self):
        return "\t".join(self.fields).lower()


    def toString(self, separator="\t"):
        return separator.join(self.fields)


    def __len__(self):
        return len(self.fields)


    def asRecord(self):
        record = []
        branch = self.parent
        while branch is not None:
            record.insert(0, branch.toString())
            branch = branch.parent
        assert record and not record[0]
        record = record[1:]
        return record + self.fields


    def field(self, column):
        assert 0 <= column <= len(self.fields)
        return self.fields[column]


class TreeOfTableModel(QAbstractItemModel):

    def __init__(self, parent=None):
        super(TreeOfTableModel, self).__init__(parent)
        self.columns = 0
        self.root = BranchNode("")
        self.headers = []
        self.nesting = 1


    # def load(self, filename, nesting, separator): 
    #     assert nesting > 0
    #     self.nesting = nesting
    #     self.root = BranchNode("")
    #     exception = None
    #     fh = None
    #     self.beginResetModel()
    #     try:
    #         for line in codecs.open(filename, "rU", "utf8"):
    #             if not line:
    #                 continue
    #             self.addRecord(line.split(separator), False)
    #     except IOError:
    #         exception = ""
    #     finally:
    #         if fh is not None:
    #             fh.close()
    #         self.endResetModel()
    #         for i in range(self.columns):
    #             self.headers.append("Column #{0}".format(i))
    #         if exception is not None:
    #             raise exception


    def addRecord(self, fields, callReset=True):
        assert len(fields) > self.nesting
        root = self.root
        branch = None
        for i in range(self.nesting):
            key = fields[i].lower()
            branch = root.childWithKey(key)
            if branch is not None:
                root = branch
            else:
                branch = BranchNode(fields[i])
                root.insertChild(branch)
                root = branch
        assert branch is not None
        items = fields[self.nesting:]
        self.columns = max(self.columns, len(items))
        branch.insertChild(LeafNode(items, branch))
        if callReset:
            self.reset()


    # def asRecord(self, index):
    #     leaf = self.nodeFromIndex(index)
    #     if leaf is not None and isinstance(leaf, LeafNode):
    #         return leaf.asRecord()
    #     return []


    def rowCount(self, parent):
        node = self.nodeFromIndex(parent)
        if node is None or isinstance(node, LeafNode):
            return 0
        return len(node)


    def columnCount(self, parent):
        return self.columns


    def data(self, index, role):
        if role == Qt.TextAlignmentRole:
            return str(int(Qt.AlignTop|Qt.AlignLeft))
        if role != Qt.DisplayRole:
            return ""
        # node = self.nodeFromIndex(index)
        node = index.internalPointer()
        assert node is not None
        if isinstance(node, BranchNode):
            return (node.toString()
                    if index.column() == 0 else "")
        return node.field(index.column())


    def headerData(self, section, orientation, role):
        if (orientation == Qt.Horizontal and
            role == Qt.DisplayRole):
            assert 0 <= section <= len(self.headers)
            return self.headers[section]
        return ""


    def index(self, row, column, parent):
        assert self.root
        branch = self.nodeFromIndex(parent)
        assert branch is not None
        return self.createIndex(row, column,
                                branch.childAtRow(row))


    def parent(self, child):
        node = self.nodeFromIndex(child)
        if node is None:
            return QModelIndex()
        parent = node.parent
        if parent is None:
            return QModelIndex()
        grandparent = parent.parent
        if grandparent is None:
            return QModelIndex()
        row = grandparent.rowOfChild(parent)
        assert row != -1
        return self.createIndex(row, 0, parent)


    def nodeFromIndex(self, index):
        return (index.internalPointer()
                if index.isValid() else self.root)


