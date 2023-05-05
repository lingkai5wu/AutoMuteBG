import threading

import pkg_resources
import pystray
from PIL import Image


class StrayUtil:
    event = None

    def __init__(self):
        self.icon = pystray.Icon("mute")
        self.icon.menu = pystray.Menu(
            pystray.MenuItem("退出", self.exit_app)
        )
        self.icon.icon = Image.open(pkg_resources.resource_filename(__name__, "../resource/mute.ico"))

    def run_app(self, event: threading.Event):
        self.event = event
        self.icon.run_detached()

    def exit_app(self):
        self.icon.stop()
        self.event.set()
