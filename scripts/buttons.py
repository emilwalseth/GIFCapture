from enum import Enum
import os
from PyQt6.QtCore import QPoint, QThread, QSize, QMimeData, QBuffer, QByteArray, QIODevice, QUrl
from PyQt6.QtGui import QIcon, QMovie, QGuiApplication, QImage
import PyQt6.QtWidgets as wgs
from scripts.settings import SettingWindow
from scripts.thread import GifThread
import scripts.saved as settings
import imageio


class ProgramState(Enum):
    IDLE = 0
    RECORDING = 1
    LOADING = 2


class Button(wgs.QPushButton):
    def __init__(self, iconPath, hoveredIconPath):
        super().__init__()

        self.regular_icon = QIcon(iconPath)
        self.hovered_icon = QIcon(hoveredIconPath)
        self.setIcon(self.regular_icon)
        self.setIconSize(QSize(50, 50))
        self.is_disabled = False
        self.setStyleSheet("""
            QPushButton
            {
                font-size: 10pt;
            }

            QPushButton:hover:!pressed
            {
                q
                icon-color: red
            }
        """)

        # For loading
        self.isLoading = False
        self.loadingGif = QMovie("data/icons/loading.gif")
        self.loadingGif.start()
        self.loadingGif.frameChanged.connect(self.updateLoading)

    def updateLoading(self):
        if self.isLoading:
            self.setIcon(QIcon(self.loadingGif.currentPixmap()))

    def setDisabled(self, value):
        self.is_disabled = value
        return super().setDisabled(value)

    def enterEvent(self, event):
        if self.is_disabled or self.isLoading:
            return

        self.setIcon(self.hovered_icon)
        return super().enterEvent(event)

    def leaveEvent(self, event):
        if self.is_disabled or self.isLoading:
            return

        self.setIcon(self.regular_icon)
        return super().leaveEvent(event)


class Buttons(wgs.QGraphicsView):

    def updateState(self, state: ProgramState):
        self.state = state
        self.record_button.isLoading = False

        if state is ProgramState.IDLE:
            # Record Button
            self.record_button.regular_icon = QIcon("data/icons/record.png")
            self.record_button.hovered_icon = QIcon(
                "data/icons/hover_record.png")
            self.record_button.setIcon(QIcon("data/icons/record.png"))
            self.record_button.setToolTip("Start recording area")

        elif state is ProgramState.RECORDING:
            # Record Button
            self.record_button.regular_icon = QIcon("data/icons/recording.png")
            self.record_button.hovered_icon = QIcon(
                "data/icons/hover_recording.png")
            self.record_button.setIcon(QIcon("data/icons/recording.png"))
            self.record_button.setToolTip("Stop recording")

        elif state is ProgramState.LOADING:

            # Record Button
            self.record_button.isLoading = True
            self.record_button.setToolTip("Saving...")

        self.mainwindow.update()

    def record(self):

        if self.state is ProgramState.RECORDING:
            # Stop Recoring if we are already recording
            print("Stop!")
            if (self.worker):
                self.worker.stop.emit()
                self.worker.deleteLater()

        else:
            self.mainwindow.lockTransform(True)
            print("Started")
            self.updateState(ProgramState.RECORDING)

            rect = self.mainwindow.selected_area.rect()

            left = round(rect.left())
            top = round(rect.top())
            width = round(rect.width())
            height = round(rect.height())

            region = {"left": left, "top": top,
                      "width": width, "height": height}

            # Create and start the screenshot thread
            self.thread = QThread()
            self.worker = GifThread(region)
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.stop.connect(self.stop_recording)
            self.worker.startSaving.connect(self.start_saving)
            self.worker.finished.connect(self.finished_recording)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.finished.connect(self.thread.quit)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.start()

    def stop_recording(self):
        if (self.worker):
            self.worker.stopped = True

    def start_saving(self):
        self.updateState(ProgramState.LOADING)

    def finished_recording(self):
        self.mainwindow.lockTransform(False)
        self.updateState(ProgramState.IDLE)

    def close(self):
        self.mainwindow.closeApp()

    def update(self, selectionrect):
        width = self.tabwidth
        buttons_pos = QPoint(round((selectionrect.bottomLeft().x() + selectionrect.bottomRight().x()) / 2) - round(width/2),
                             round(selectionrect.bottomLeft().y() + 15))
        self.move(buttons_pos)

    def browse(self):
        file_path = settings.GlobalSettings.value(
            settings.SETTING_SAVEDIRECTORY, settings.defaultDirectory)

        if not os.path.exists(file_path):
            os.mkdir(file_path)

        os.startfile(file_path)

    def openSettings(self):

        settings_dialog = SettingWindow()
        settings_dialog.exec()

    def copy(self):

        file_path = settings.GlobalSettings.value(
            settings.SETTING_SAVEDIRECTORY, settings.defaultDirectory)

        file_list = os.listdir(file_path)
        last_file = os.path.join(file_path, file_list[-1])

        clipboard = QGuiApplication.clipboard()
        clipboard.setImage(QImage(last_file))

        print("Copied!")

    def save(self):
        file_path, _ = wgs.QFileDialog.getSaveFileName(
            None, "Save GIF", "my_gif.gif", "GIF Files (*.gif)"
        )
        imageio.save(file_path, "GIF")

    def __init__(self, scene, mainwindow: wgs.QWidget):
        super().__init__()
        self.setScene(scene)
        self.setVisible(False)
        self.mainwindow = mainwindow
        self.tabwidth = 500
        self.tabheight = 90
        self.setStyleSheet(
            "background-color: white; border-radius: 10px; opacity: 0.4")
        self.setGeometry(0, 0, self.tabwidth, self.tabheight)
        self.state = ProgramState.IDLE

        # Record Button
        self.record_button = Button(
            "data/icons/record.png", "data/icons/hover_record.png")
        self.updateState(ProgramState.IDLE)
        self.record_button.clicked.connect(self.record)

        # Settings Button
        self.settings_button = Button(
            "data/icons/settings.png", "data/icons/hover_settings.png")
        self.settings_button.setToolTip("Settings")
        self.settings_button.clicked.connect(self.openSettings)

        # Close Button
        self.close_button = Button(
            "data/icons/cross.png", "data/icons/hover_cross.png")
        self.close_button.setToolTip("Exit")
        self.close_button.clicked.connect(self.close)

        # Copy Button
        # self.copy_button = Button(
        #     "data/icons/copy.png", "data/icons/hover_copy.png")
        # self.copy_button.setToolTip("Copy GIF")
        # self.copy_button.setDisabled(True)
        # self.copy_button.clicked.connect(self.copy)

        # Save Button
        # self.save_button = Button(
        #     "data/icons/save.png", "data/icons/hover_save.png")
        # self.save_button.setToolTip("Save GIF")
        # self.save_button.setDisabled(True)
        # self.save_button.clicked.connect(self.save)

        # Browse Button
        self.browse_button = Button(
            "data/icons/browse.png", "data/icons/hover_browse.png")
        self.browse_button.setToolTip("Browse GIFs")
        self.browse_button.clicked.connect(self.browse)

        layout = wgs.QHBoxLayout()
        layout.addWidget(self.record_button)
        layout.addWidget(self.settings_button)
        layout.addWidget(self.browse_button)
        layout.addWidget(self.close_button)

        self.setLayout(layout)
