import threading

import pkg_resources
import pystray
from PIL import Image


def on_icon_ready(icon):
    icon.visible = True
    icon.notify("游戏关闭后自动退出，或从任务栏退出", "后台静音启动成功")


class StrayUtil:
    event = None

    def __init__(self):
        name = "后台静音"
        menu = pystray.Menu(
            pystray.MenuItem("退出", self.exit_app)
        )
        icon = Image.open(pkg_resources.resource_filename(__name__, "../resource/mute.ico"))
        self.icon = pystray.Icon(name, icon, name, menu)

    def run_app(self, event: threading.Event):
        self.event = event
        self.icon.run_detached(on_icon_ready)

    def exit_app(self):
        self.icon.stop()
        self.event.set()
