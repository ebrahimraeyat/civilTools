from PySide2.QtWidgets import QWidget

def set_children_enabled(parent, enabled):
    """Set the enabled state of all children of the given parent widget."""
    for child in parent.findChildren(QWidget):
        child.setEnabled(enabled)