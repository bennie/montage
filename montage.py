""" Draw an Image Montage """

import hashlib
import os.path

from pathlib import Path

import pickledb

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
    Qt,
)
from wand.image import Image

import yaml

from lib.montage import is_image, makethumb


class Worker(QObject):
    """Background worker for image processing"""

    finished = pyqtSignal()
    progress = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config

    def scan_for_files(self):
        """Long-running task."""
        for path in Path(self.config["imagedir"]).rglob("*"):
            if not path.is_file():
                continue
            if not is_image(path.name):
                continue
            self.progress.emit(str(path))
        self.finished.emit()

    def make_thumbnails(self):
        """Long-running task."""
        for file in self.config["files"]:
            path = Path(file)
            md5 = hashlib.md5(str(path).encode()).hexdigest()
            outfile = os.path.join(
                self.config["thumbdir"], f"{md5}.{self.config['thumbnail_type']}"
            )
            outfile_vid = os.path.join(
                self.config["thumbdir"], f"{md5}-0.{self.config['thumbnail_type']}"
            )
            if not Path(outfile).is_file() and not Path(outfile_vid).is_file():
                makethumb(
                    path,
                    outfile,
                    self.config["height_ratio"],
                    self.config["pref_width"],
                    self.config["pref_height"],
                )
            self.progress.emit(md5)
        self.finished.emit()

    def make_color_db(self):
        """Long-running task."""
        cache = self.config["color_db"]

        for path in Path(self.config["thumbdir"]).rglob("*.png"):
            if not path.is_file():
                continue

            if cache.exists(str(path)):
                self.progress.emit("cache hit.")
                continue

            count = 0
            count_red = 0
            count_green = 0
            count_blue = 0

            try:
                with Image(filename=path) as img:
                    maxima = img.maxima
                    if maxima < 65535:
                        print(f"NOPE (depth is {maxima}) on {path}")
                        continue

                    blob = img.make_blob(format="RGB")
                    for cursor in range(0, img.width * img.height * 3, 3):
                        count_red += blob[cursor]
                        count_green += blob[cursor + 1]
                        count_blue += blob[cursor + 2]
                        count += 1

                av_r = int(count_red / count)
                av_g = int(count_green / count)
                av_b = int(count_blue / count)

                cache.set(str(path), [av_r, av_g, av_b])
                self.progress.emit(
                    f"{av_r:03.0f} {av_g:03.0f} {av_b:03.0f} ({maxima:03.0f}) : {path}"
                )
            except IndexError:
                print(f"NOPE on {path}")

        cache.dump()
        print(f"{cache.totalkeys()} items in the cache")
        self.finished.emit()


class Window(QWidget):  # pylint: disable=too-many-instance-attributes
    """Main app class"""

    def __init__(self):
        super().__init__()

        self.files = []
        self.thread = None
        self.worker = None

        with open("config.yaml", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        self.draw_ui()

    def draw_ui(self):
        """draw the main app window"""
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

        self.macro_progress_label = QLabel("Select files above")
        self.macro_progress_bar = QProgressBar()
        self.macro_progress_bar.setRange(0, 5)

        self.progress_label = QLabel("")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 1)

        self.status_text = QLabel("")
        self.status_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QGridLayout()
        layout.addWidget(self.imagedir, 0, 0)
        layout.addWidget(self.imagedir_label, 0, 1)
        layout.addWidget(self.cache, 1, 0)
        layout.addWidget(self.cache_label, 1, 1)
        layout.addWidget(self.goal, 2, 0)
        layout.addWidget(self.goal_label, 2, 1)
        layout.addWidget(self.macro_progress_label, 3, 0)
        layout.addWidget(self.macro_progress_bar, 3, 1)
        layout.addWidget(self.progress_label, 4, 0)
        layout.addWidget(self.progress_bar, 4, 1)
        layout.addWidget(self.status_text, 5, 0, 1, 2)

        self.setLayout(layout)

    def check_status(self):
        """Check if we have picked the directories and can start processing

        If we are good, calculate default sizes and write data into the config.
        Then start the image scan.
        """
        if (
            os.path.exists(self.imagedir_label.text())
            and os.path.exists(self.cache_label.text())
            and os.path.isfile(self.goal_label.text())
        ):

            self.config["imgdir"] = self.imagedir_label.text()
            self.config["thumbdir"] = self.cache_label.text()
            self.config["goal"] = self.goal_label.text()

            self.config["color_db_file"] = os.path.join(
                self.config["thumbdir"], "palette.db"
            )
            self.config["color_db"] = pickledb.load(self.config["color_db_file"], False)

            with Image(filename=self.config["goal"]) as img:
                self.config["height_ratio"] = img.height / img.width
                self.config["pref_width"] = self.config["default_size"]
                self.config["pref_height"] = int(
                    self.config["default_size"] * self.config["height_ratio"]
                )

            self.scan_for_files()

    def scan_for_files(self):
        """Crawl the file system to determine a list of files to examine"""
        self.thread = QThread()
        self.worker = Worker(self.config)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.scan_for_files)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.scan_for_files_progress)
        self.thread.start()

        self.imagedir.setEnabled(False)
        self.cache.setEnabled(False)
        self.goal.setEnabled(False)

        self.macro_progress_bar.setValue(1)
        self.macro_progress_label.setText("Finding files... ")
        self.progress_bar.setRange(0, 0)

        self.thread.finished.connect(
            lambda: self.scan_for_files_done()  # pylint: disable=unnecessary-lambda
        )

    def scan_for_files_progress(self, n):
        """Update progress; stub for now"""
        self.files.append(n)
        self.status_text.setText(f"{n[-25:]:25}")

    def scan_for_files_done(self):
        """We've found all the files, start processing"""
        self.progress_bar.setRange(0, len(self.files))
        self.progress_label.setText(f"{len(self.files)} files found")
        self.status_text.setText("")

        self.cache_files()

    def cache_files(self):
        """Go through the file-list and create thumnails in the cache"""
        self.config["files"] = self.files  # This can't be good

        self.thread = QThread()
        self.worker = Worker(self.config)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.make_thumbnails)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.cache_files_progress)
        self.thread.start()

        self.imagedir.setEnabled(False)
        self.cache.setEnabled(False)
        self.goal.setEnabled(False)

        self.macro_progress_bar.setValue(2)
        self.macro_progress_label.setText("Caching images... ")
        self.progress_bar.setRange(0, len(self.files))

        self.thread.finished.connect(
            lambda: self.cache_files_done()  # pylint: disable=unnecessary-lambda
        )

    def cache_files_progress(self, md5val):
        """Update progress; stub for now"""
        self.status_text.setText(f"{md5val}")
        newval = self.progress_bar.value() + 1
        self.progress_label.setText(f"{newval} / {len(self.files)}")
        self.progress_bar.setValue(newval)

    def cache_files_done(self):
        """We've found all the files, start processing"""
        self.progress_label.setText(f"{len(self.files)} files cached.")
        self.status_text.setText("")

        self.color_db()

    def color_db(self):
        """Go through the file-list and create thumnails in the cache"""
        self.config["files"] = self.files  # This can't be good

        self.thread = QThread()
        self.worker = Worker(self.config)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.make_color_db)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.color_db_progress)
        self.thread.start()

        self.imagedir.setEnabled(False)
        self.cache.setEnabled(False)
        self.goal.setEnabled(False)

        self.macro_progress_bar.setValue(3)
        self.macro_progress_label.setText("Analyzing colors... ")
        self.progress_bar.setRange(0, len(self.files))
        self.progress_bar.setValue(0)

        self.thread.finished.connect(
            lambda: self.color_db_done()  # pylint: disable=unnecessary-lambda
        )

    def color_db_progress(self, _):
        """Update progress; stub for now"""
        newval = self.progress_bar.value() + 1
        self.progress_label.setText(f"{newval} / {len(self.files)}")
        self.progress_bar.setValue(newval)

    def color_db_done(self):
        """We've found all the files, start processing"""
        self.status_text.setText(f"{len(self.files)} files analyzed.")

        self.render_montage()

    def render_montage(self):
        """Draw the montage!"""
        self.macro_progress_bar.setValue(4)
        self.macro_progress_label.setText("Rendering montage... ")
        self.progress_bar.setRange(0, len(self.files))
        self.progress_bar.setValue(0)

        self.progress_label.setText("")
        self.status_text.setText("")

        #self.thread.finished.connect(
        #    lambda: self.render_montage_done()  # pylint: disable=unnecessary-lambda
        #)

        self.render_montage_done()

    def render_montage_done(self):
        """All done."""

        self.macro_progress_bar.setValue(5)
        self.macro_progress_label.setText("")
        self.status_text.setText("Montage completed.")
        self.progress_bar.setValue(0)

    @pyqtSlot()
    def get_dir(self, label):
        """Dialog to select a directory"""
        fname = QFileDialog.getExistingDirectory(
            self, "Select an input directory", "${HOME}"
        )
        label.setText(fname)
        self.check_status()

    @pyqtSlot()
    def get_file(self):
        """Dialog to select the goal file"""
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
