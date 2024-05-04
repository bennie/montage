""" Draw an Image Montage """

import os.path

from pathlib import Path
from PyQt6.QtWidgets import (  # pylint: disable=no-name-in-module
    QApplication,
    QFileDialog,
    QGridLayout,
    QLabel,
    QProgressBar,
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

from lib.montage import is_image

class Worker(QObject):  # pylint: disable=too-few-public-methods
    """ Background worker for image processing """
    finished = pyqtSignal()
    progress = pyqtSignal(str)

    def __init__(self, imagedir):
        super().__init__()
        self.imagedir = imagedir

    def run(self):
        """Long-running task."""
        for path in Path(self.imagedir).rglob('*'):
            if not path.is_file():
                continue
            if not is_image(path.name):
                continue

            self.progress.emit(str(path))


            #md5 = hashlib.md5(str(path).encode()).hexdigest()
            #outfile = os.path.join(config['thumbdir'], f"{md5}.{config['thumbnail_type']}")

            #makethumb(path, outfile, height_ratio, pref_width, pref_height)

        self.finished.emit()

class Window(QWidget):  # pylint: disable=too-many-instance-attributes
    """ Main app class """
    def __init__(self):
        super().__init__()

        self.files = []
        self.thread = None
        self.worker = None

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
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0,1)

        self.status_text =  QLabel("")
        self.status_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QGridLayout()
        layout.addWidget(self.imagedir, 0, 0)
        layout.addWidget(self.imagedir_label, 0, 1)
        layout.addWidget(self.cache, 1, 0)
        layout.addWidget(self.cache_label, 1, 1)
        layout.addWidget(self.goal, 2, 0)
        layout.addWidget(self.goal_label, 2, 1)
        layout.addWidget(self.progress_label, 3, 0)
        layout.addWidget(self.progress_bar, 3, 1)
        layout.addWidget(self.status_text, 4, 0, 1, 2)

        self.setLayout(layout)

    def check_status(self):
        """ Check if we have selected valid entries and can proceed to processing """
        if os.path.exists(self.imagedir_label.text()) and \
           os.path.exists(self.cache_label.text()) and \
           os.path.isfile(self.goal_label.text()):
            self.run_long_task(self.imagedir_label.text())

    def run_long_task(self, imagedir):
        """ A long running task to test """
        self.thread = QThread()
        self.worker = Worker(imagedir)
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
        self.progress_bar.setRange(0,0)
        self.progress_label.setText("Finding files... ")

        self.thread.finished.connect(lambda: self.diediedie())  # pylint: disable=unnecessary-lambda

    def diediedie(self):
        """ Go Bye-Bye """
        self.progress_bar.setRange(0,1)
        self.progress_label.setText(f"{len(self.files)} files found")
        self.status_text.setText("")

    def report_progress(self, n):
        """ Update progress; stub for now """
        self.files.append(n)
        self.status_text.setText(f"{n[-25:]:25}")

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
