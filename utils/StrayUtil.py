import threading
import webbrowser

import pkg_resources
import pystray
from PIL import Image

from utils.ConfigUtil import ConfigUtil


def _open_site():
    webbrowser.open('https://gitee.com/lingkai5wu/AutoMuteBG')


class StrayUtil:
    def __init__(self, run_util):
        self.event = None
        self.run_util = run_util

        name = "后台静音"
        menu = pystray.Menu(
            pystray.MenuItem("开源地址", _open_site),
            pystray.MenuItem("重新加载", self._reload),
            pystray.MenuItem("退出", self.exit_app)
        )
        icon = Image.open(pkg_resources.resource_filename(__name__, "../resource/mute.ico"))

        self.icon = pystray.Icon(name, icon, name, menu)

    def run_detached(self, event: threading.Event):
        def on_icon_ready(icon):
            icon.visible = True
            icon.notify("启动成功")

        self.event = event
        self.icon.run_detached(on_icon_ready)

    def _reload(self):
        config_util = ConfigUtil()
        self.run_util.start_audio_control_threads(config_util)
        self.icon.notify("重新加载成功")

    def exit_app(self):
        self.icon.stop()
        self.event.set()
