import sys
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QProgressBar, QLabel

StyleSheet = '''
#RedProgressBar {
    text-align: center;
    border-radius: 8px;
}
#RedProgressBar::chunk {
    background-color: #F44336;
    border-radius: 8px;
}
#GreenProgressBar {
    min-height: 12px;
    max-height: 12px;
    border-radius: 6px;
}
#GreenProgressBar::chunk {
    border-radius: 6px;
    background-color: #009688;
}
#BlueProgressBar {
    border: 2px solid #2196F3;
    border-radius: 5px;
    background-color: #E0E0E0;
}
#BlueProgressBar::chunk {
    background-color: #2196F3;
    width: 10px; 
    margin: 0.5px;
}
'''




class Window(QWidget):

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.resize(600, 200)
        layout = QVBoxLayout(self)
        self.label = QLabel()
        layout.addWidget(self.label)
        layout.addWidget(
            QProgressBar(self, minimum=0, maximum=0, textVisible=False,
                        objectName="GreenProgressBar"))


def show(text=None):
    app = QApplication(sys.argv)
    app.setStyleSheet(StyleSheet)
    w = Window()
    if text:
        w.label.setText(text)
    w.show()
    return w, app
    # sys.exit(app.exec_())

if __name__ == "__main__":
    show()