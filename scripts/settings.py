import os
from PyQt6.QtCore import Qt, QSize, QKeyCombination, pyqtSignal
from PyQt6.QtGui import QPalette
import PyQt6.QtWidgets as wgs
import scripts.saved as settings


FONT_SIZE = "12pt"


class SettingWindow(wgs.QDialog):

    refresh = pyqtSignal()
    save = pyqtSignal()

    def saveOptimize(self):
        current = self.optimizing_group.isChecked()
        settings.GlobalSettings.setValue(settings.SETTING_OPTIMIZING, current)

    def refreshOptimize(self):
        default = settings.defaultOptimizing
        current = settings.GlobalSettings.value(
            settings.SETTING_OPTIMIZING, defaultValue=default, type=bool)
        self.optimizing_group.setChecked(current)

    def __init__(self):
        super().__init__()

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.setMinimumWidth(800)
        self.setStyleSheet(f"font-size: {FONT_SIZE}")
        self.refresh.connect(self.refreshOptimize)
        self.save.connect(self.saveOptimize)
        # Optimizing Group
        self.optimizing_group_layout = wgs.QVBoxLayout()

        # Settings Elements
        resolution = Resolution(self)
        fps = FPS(self)
        compression = Compression(self)

        self.optimizing_group_layout.addItem(resolution)
        self.optimizing_group_layout.addItem(fps)
        self.optimizing_group_layout.addItem(compression)
        self.optimizing_group_layout.setSpacing(20)

        self.optimizing_group = SettingsGroup("Optimization")
        self.optimizing_group.setCheckable(True)
        self.refreshOptimize()
        self.optimizing_group.setLayout(self.optimizing_group_layout)

        # General Group
        self.general_group_layout = wgs.QVBoxLayout()

        # Settings Elements
        starup = StartupLaunch(self)
        shortcut = Shortcut(self)
        saveDir = SaveDirectory(self)

        # self.general_group_layout.addItem(starup)
        # self.general_group_layout.addItem(shortcut)
        self.general_group_layout.addItem(saveDir)
        self.general_group = SettingsGroup("General")
        self.general_group_layout.setSpacing(20)
        self.general_group.setLayout(self.general_group_layout)

        # Settings Menu Layout
        self.layout = wgs.QVBoxLayout()
        self.footer = FooterButtons(self)
        self.layout.setSpacing(30)
        self.layout.addWidget(self.optimizing_group)
        self.layout.addWidget(self.general_group)
        self.layout.addStretch(1)
        self.layout.addItem(self.footer)

        self.setLayout(self.layout)


class SettingsGroup(wgs.QGroupBox):
    def __init__(self, title: str):
        super().__init__()
        self.setTitle(title)

        with open('data\styles\settings_group.css', 'r') as style:
            css = style.read()

        self.setStyleSheet(css)


class SettingsLabel(wgs.QLabel):
    def __init__(self, text):
        super().__init__()

        self.setText(text)


class SettingsSpinBox(wgs.QSpinBox):
    def __init__(self, min: int, max: int, current: int, suffix: str):
        super().__init__()

        self.setMaximum(max)
        self.setValue(current)
        self.setMinimum(min)
        self.setSuffix(suffix)
        self.setFixedWidth(100)
        self.setAlignment(Qt.AlignmentFlag.AlignRight)


class SettingsSlider(wgs.QWidget):
    def __init__(self, min: int, max: int, current: int, labelSuffix: str):
        super().__init__()

        self.labelSuffix = labelSuffix
        self.slider = wgs.QSlider(Qt.Orientation.Horizontal)
        self.slider.setMaximum(max)
        self.slider.setValue(current)
        self.slider.setTickPosition(wgs.QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(10)
        self.slider.setMinimum(min)
        self.slider.setFixedWidth(200)
        self.slider.valueChanged.connect(self.updateLabel)

        self.label = SettingsLabel(str(self.slider.value()) + self.labelSuffix)

        layout = wgs.QHBoxLayout()
        layout.setSpacing(5)

        layout.addWidget(self.label)
        layout.addWidget(self.slider)

        self.setLayout(layout)

    def updateLabel(self, newValue: int):
        self.label.setText(str(newValue) + self.labelSuffix)


class Resolution(wgs.QHBoxLayout):
    def __init__(self, window: SettingWindow):
        super().__init__()

        window.refresh.connect(self.refresh)
        window.save.connect(self.save)

        text = SettingsLabel("Resolution:")
        self.slider = SettingsSlider(1, 100, 0, "%")

        self.refresh()

        self.addWidget(text)
        self.addStretch(1)
        self.addWidget(self.slider)

    def save(self):
        current = self.slider.slider.value() / 100
        settings.GlobalSettings.setValue(settings.SETTING_RESOLUTION, current)

    def refresh(self):

        default = settings.defaultResolution
        current = settings.GlobalSettings.value(
            settings.SETTING_RESOLUTION, defaultValue=default, type=float)
        self.slider.slider.setValue(round(current*100))


class FPS(wgs.QHBoxLayout):
    def __init__(self, window: SettingWindow):
        super().__init__()

        window.refresh.connect(self.refresh)
        window.save.connect(self.save)

        text = SettingsLabel("FPS:")
        self.slider = SettingsSlider(1, 24, 1, "")

        self.refresh()

        self.addWidget(text)
        self.addStretch(1)
        self.addWidget(self.slider)

    def save(self):
        current = self.slider.slider.value()
        settings.GlobalSettings.setValue(settings.SETTING_FPS, current)

    def refresh(self):
        default = settings.defaultFps
        current = settings.GlobalSettings.value(
            settings.SETTING_FPS, defaultValue=default)
        self.slider.slider.setValue(current)


class Compression(wgs.QHBoxLayout):
    def __init__(self, window: SettingWindow):
        super().__init__()

        window.refresh.connect(self.refresh)
        window.save.connect(self.save)

        text = SettingsLabel("Compression:")
        self.slider = SettingsSlider(1, 200, 1, "")

        self.refresh()

        self.addWidget(text)
        self.addStretch(1)
        self.addWidget(self.slider)

    def save(self):
        current = self.slider.slider.value()
        settings.GlobalSettings.setValue(settings.SETTING_COMPRESSION, current)

    def refresh(self):
        default = settings.defaultCompression
        current = settings.GlobalSettings.value(
            settings.SETTING_COMPRESSION, defaultValue=default)
        self.slider.slider.setValue(current)


class Shortcut(wgs.QHBoxLayout):
    def __init__(self, window: SettingWindow):
        super().__init__()

        window.refresh.connect(self.refresh)
        window.save.connect(self.save)

        text = SettingsLabel("Hot-key:")
        self.key = wgs.QKeySequenceEdit()

        self.refresh()

        self.addWidget(text)
        self.addStretch(1)
        self.addWidget(self.key)

    def save(self):
        current = self.key.keySequence().toString()
        settings.GlobalSettings.setValue(settings.SETTING_SHORTCUT, current)

    def refresh(self):
        default = settings.defaultShortcut
        current = settings.GlobalSettings.value(
            settings.SETTING_SHORTCUT, defaultValue=default)
        self.key.setKeySequence(current)


class SaveDirectory(wgs.QHBoxLayout):
    def __init__(self, window: SettingWindow):
        super().__init__()

        window.refresh.connect(self.refresh)
        window.save.connect(self.save)

        text = SettingsLabel("Save Directory:")
        self.dir = wgs.QLabel("")
        button = SettingsButton("...")
        button.clicked.connect(self.chooseDir)

        self.refresh()

        self.addWidget(text)
        self.addStretch(1)
        self.addWidget(self.dir)
        self.addWidget(button)

    def chooseDir(self):

        olddir = self.dir.text()

        newdir = str(wgs.QFileDialog.getExistingDirectory(
            directory=olddir, caption="Select Directory"))

        if newdir != "":
            self.dir.setText(newdir)

    def save(self):
        current = self.dir.text()
        settings.GlobalSettings.setValue(
            settings.SETTING_SAVEDIRECTORY, current)

    def refresh(self):
        default = settings.defaultDirectory
        current = settings.GlobalSettings.value(
            settings.SETTING_SAVEDIRECTORY, defaultValue=default)

        new_dir = current.replace("\\", "/")

        if not os.path.exists(new_dir):
            os.mkdir(new_dir)

        self.dir.setText(new_dir)


class StartupLaunch(wgs.QHBoxLayout):
    def __init__(self, window: SettingWindow):
        super().__init__()

        window.refresh.connect(self.refresh)
        window.save.connect(self.save)

        text = SettingsLabel("Launch on startup:")

        self.checkbox = wgs.QCheckBox()

        self.refresh()

        self.checkbox.setGeometry(0, 0, 200, 200)
        self.addWidget(text)
        self.addStretch(1)
        self.addWidget(self.checkbox)

    def save(self):
        current = self.checkbox.isChecked()
        settings.GlobalSettings.setValue(settings.SETTING_STARTUP, current)

    def refresh(self):
        default = settings.defaultStartup
        current = settings.GlobalSettings.value(
            settings.SETTING_STARTUP, defaultValue=default, type=bool)
        self.checkbox.setChecked(current)


class SettingsButton(wgs.QPushButton):
    def __init__(self, text: str):
        super().__init__()

        self.setText(text)
        self.setFlat(True)


class FooterButtons(wgs.QHBoxLayout):
    def __init__(self, settingsmenu: SettingWindow):
        super().__init__()
        self.settings = settingsmenu

        apply = SettingsButton("Ok")
        apply.clicked.connect(self.save)

        reset = SettingsButton("Reset to Default")
        reset.clicked.connect(self.reset)

        cancel = SettingsButton("Cancel")
        cancel.clicked.connect(self.close)

        self.addWidget(apply)
        self.addWidget(reset)
        self.addWidget(cancel)

    def save(self):
        self.settings.save.emit()
        self.settings.close()

    def reset(self):
        settings.resetSettingsToDefault()
        self.settings.refresh.emit()

    def close(self):
        self.settings.close()


os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"

if __name__ == '__main__':

    app = wgs.QApplication([])
    app.setStyle("Fusion")
    mw = SettingWindow()
    mw.show()
    app.exec()
