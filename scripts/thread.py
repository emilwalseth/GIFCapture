import os
from PyQt6.QtCore import QObject, pyqtSignal
import imageio
import time
import mss
from PIL import Image
from pygifsicle import gifsicle
from scripts.saved import GlobalSettings
import scripts.saved as settings


class GifThread(QObject):

    finished = pyqtSignal()
    stop = pyqtSignal()
    startSaving = pyqtSignal()

    def __init__(self, region):
        super().__init__()
        self.region = region
        self.stopped = False

    def run(self):
        screenshots = []
        fps = GlobalSettings.value(settings.SETTING_FPS, settings.defaultFps)
        scale_factor = GlobalSettings.value(
            settings.SETTING_RESOLUTION, settings.defaultResolution)
        should_optimize = GlobalSettings.value(
            settings.SETTING_OPTIMIZING, settings.defaultOptimizing)
        lossiness = GlobalSettings.value(
            settings.SETTING_COMPRESSION, settings.defaultCompression)
        time.sleep(0.3)

        # Make Path
        path = GlobalSettings.value(
            settings.SETTING_SAVEDIRECTORY, settings.defaultDirectory)
        num = len(os.listdir(path))
        filename = f"/gif_{num}.gif"

        path = path + filename

        print(path)

        print("Running")
        with mss.mss() as sct:
            while not self.stopped:
                # Get raw pixels from the screen, save it to a Numpy array
                screenshot = sct.grab(self.region)
                # Convert to a PIL Image
                image = Image.frombytes(
                    "RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

                image = image.convert(dither=Image.Dither.NONE)

                screenshots.append(image)
                time.sleep(1/fps)

        self.startSaving.emit()

        imageio.mimsave(path, screenshots,
                        duration=1/fps)

        # If we are optimizing our image, do it
        if should_optimize:
            gifsicle(sources=path, colors=256,
                     optimize=True, options=[f"--lossy={lossiness}", "--scale", str(scale_factor)])

        print("Done")
        self.finished.emit()
