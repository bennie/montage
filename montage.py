""" Draw an Image Montage """

import os.path

from time import sleep

from PyQt6.QtWidgets import (  # pylint: disable=no-name-in-module
    QApplication,
    QFileDialog,
    QGridLayout,
    QLabel,
    QPushButton,
    QWidget,
)
from PyQt6.QtCore import (  # pylint: disable=no-name-in-module
    pyqtSignal,
    pyqtSlot,
    QObject,
    QThread,
    Qt
)

class Worker(QObject):
    """ Background worker for image processing """
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def run(self):
        """Long-running task."""
        for i in range(5):
            sleep(1)
            self.progress.emit(i + 1)
        self.finished.emit()

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

        self.progress_label = QLabel("Select files above")

        layout = QGridLayout()
        layout.addWidget(self.imagedir, 0, 0)
        layout.addWidget(self.imagedir_label, 0, 1)
        layout.addWidget(self.cache, 1, 0)
        layout.addWidget(self.cache_label, 1, 1)
        layout.addWidget(self.goal, 2, 0)
        layout.addWidget(self.goal_label, 2, 1)
        layout.addWidget(self.progress_label, 3, 0, 1, 2)

        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def check_status(self):
        """ Check if we have selected valid entries and can proceed to processing """
        if os.path.exists(self.imagedir_label.text()) and \
           os.path.exists(self.cache_label.text()) and \
           os.path.isfile(self.goal_label.text()):
            self.run_long_task()

    def run_long_task(self):
        """ A long running task to test """
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.report_progress)
        self.thread.start()

        self.imagedir.setEnabled(False)
        self.cache.setEnabled(False)
        self.goal.setEnabled(False)

        self.thread.finished.connect(lambda: self.diediedie())

    def diediedie(self):
        """ Go Bye-Bye """
        print("Exited...")
        app.quit()

    def report_progress(self, n):
        """ Update progress; stub for now """
        self.progress_label.setText(f"Progress Update... {n}")

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
