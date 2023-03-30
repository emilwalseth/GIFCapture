import os
from PyQt6.QtCore import QSettings


SETTING_OPTIMIZING = "optimizing"
SETTING_RESOLUTION = "resolution"
SETTING_FPS = "fps"
SETTING_COMPRESSION = "compression"
SETTING_STARTUP = "startup"
SETTING_SHORTCUT = "shortcut"
SETTING_SAVEDIRECTORY = "directory"


GlobalSettings = QSettings("gifcapture", "gifcapture")


# Get the path to the pictures folder
pictures_folder = os.path.expanduser("~/Pictures/GifCapture")

# Replace the username with the current user's username
pictures_folder = pictures_folder.replace(
    "~", os.path.expanduser("~").replace('\\', "/"))

# Defaults

defaultOptimizing = True
defaultResolution = 0.75
defaultFps = 15
defaultCompression = 35
defaultStartup = True
defaultShortcut = "Ctrl+Shift+R"
defaultDirectory = pictures_folder


def resetSettingsToDefault():
    GlobalSettings.setValue(SETTING_OPTIMIZING, defaultOptimizing)
    GlobalSettings.setValue(SETTING_RESOLUTION, defaultResolution)
    GlobalSettings.setValue(SETTING_FPS, defaultFps)
    GlobalSettings.setValue(SETTING_COMPRESSION, defaultCompression)
    GlobalSettings.setValue(SETTING_STARTUP, defaultStartup)
    GlobalSettings.setValue(SETTING_SHORTCUT, defaultShortcut)
    GlobalSettings.setValue(SETTING_SAVEDIRECTORY, defaultDirectory)
