""" Draw an Image Montage """

import os.path

from PyQt6.QtWidgets import (  # pylint: disable=no-name-in-module
    QApplication,
    QFileDialog,
    QPushButton,
    QGridLayout,
    QWidget,
    QLabel
)
from PyQt6.QtCore import pyqtSlot  # pylint: disable=no-name-in-module

class Window(QWidget):
    """ Main app class """

    def __init__(self):
        super().__init__()
        self.draw_ui()

    def draw_ui(self):
        """ draw the main app window """
        self.setWindowTitle("Montage Builder")

        self.imagedir_label = QLabel("Pick a Directory")
        self.imagedir = QPushButton("Image Directory")
        self.imagedir.clicked.connect(lambda: self.get_dir(self.imagedir_label))

        self.cache_label = QLabel("Pick a Cache Directory")
        self.cache = QPushButton("Cache Directory")
        self.cache.clicked.connect(lambda: self.get_dir(self.cache_label))

        self.goal = QPushButton("Goal Image")
        self.goal.clicked.connect(self.get_file)
        self.goal_label = QLabel("Pick a Image")

        layout = QGridLayout()
        layout.addWidget(self.imagedir, 0, 0)
        layout.addWidget(self.imagedir_label, 0, 1)
        layout.addWidget(self.cache, 1, 0)
        layout.addWidget(self.cache_label, 1, 1)
        layout.addWidget(self.goal, 2, 0)
        layout.addWidget(self.goal_label, 2, 1)
        self.setLayout(layout)

    def check_status(self):
        """ Check if we have selected valid entries and can proceed to processing """
        if os.path.exists(self.imagedir_label.text()) and \
           os.path.exists(self.cache_label.text()) and \
           os.path.isfile(self.goal_label.text()):
            print("Exited...")
            app.quit()

    @pyqtSlot()
    def get_dir(self, label):
        """ Dialog to select a directory """
        fname = QFileDialog.getExistingDirectory(
            self,
            "Select an input directory",
            "${HOME}"
        )
        label.setText(fname)
        self.check_status()

    @pyqtSlot()
    def get_file(self):
        """ Dialog to select the goal file """
        fname = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "${HOME}",
            "All Files (*);; Python Files (*.py);; PNG Files (*.png)",
        )
        self.goal_label.setText(fname[0])
        self.check_status()


app = QApplication([])
window = Window()
window.show()
app.exec()
