""" Draw an Image Montage """

from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QPushButton,
    QGridLayout,
    QWidget,
    QLabel
)
from PyQt6.QtCore import pyqtSlot

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Montage Builder")

        self.imagedir = QPushButton("Image Directory")
        self.imagedir.clicked.connect(self.get_dir)
        self.imagedir_label = QLabel("Pick a Directory")

        self.goal = QPushButton("Goal Image")
        self.goal.clicked.connect(self.get_file)
        self.goal_label = QLabel("Pick a Image")

        layout = QGridLayout()
        layout.addWidget(self.imagedir, 0, 0)
        layout.addWidget(self.imagedir_label, 0, 1)
        layout.addWidget(self.goal, 1, 0)
        layout.addWidget(self.goal_label, 1, 1)
        self.setLayout(layout)

    @pyqtSlot()
    def get_dir(self):
        fname = QFileDialog.getExistingDirectory(
            self,
            "Select an input directory",
            "${HOME}"
        )
        self.imagedir_label.setText(fname)

    @pyqtSlot()
    def get_file(self):
        fname = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "${HOME}",
            "All Files (*);; Python Files (*.py);; PNG Files (*.png)",
        )
        self.goal_label.setText(fname[0])


app = QApplication([])
window = Window()
window.show()
app.exec()
