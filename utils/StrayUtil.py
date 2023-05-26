import os
import threading
import webbrowser

import pkg_resources
import pystray
from PIL import Image

from utils.AudioUtil import save_process_name_to_txt
from utils.ConfigUtil import ConfigUtil
from utils.LoggerUtil import get_log_dir


def _open_site():
    webbrowser.open('https://gitee.com/lingkai5wu/AutoMuteBG')


class StrayUtil:
    def __init__(self, run_util, stray_setup_msg, logger):
        self.run_util = run_util
        self.stray_setup_msg = stray_setup_msg
        self.logger = logger
        self.event = None

        name = "后台静音"
        menu = pystray.Menu(
            pystray.MenuItem("开源地址", _open_site),
            pystray.MenuItem("日志文件", self._open_log_folder),
            pystray.MenuItem("查看进程", save_process_name_to_txt),
            pystray.MenuItem("重新加载", self._reload),
            pystray.MenuItem("退出", self.exit_app)
        )
        icon = Image.open(pkg_resources.resource_filename(__name__, "../resource/mute.ico"))

        self.icon = pystray.Icon(name, icon, name, menu)

    def run_detached(self, event):
        def on_icon_ready(icon):
            icon.visible = True
            if self.stray_setup_msg:
                icon.notify("启动成功")
            threading.current_thread().setName("StrayRunCallbackThread")
            self.logger.info("Stray is running.")

        self.event = event
        self.logger.info("Starting stray.")
        threading.Thread(target=self.icon.run, args=(on_icon_ready,), name="StrayThread").start()

    def _open_log_folder(self):
        log_path = get_log_dir()
        try:
            os.startfile(log_path)
        except FileNotFoundError:
            self.icon.notify("请检查配置文件中的 setting.max_log_files", "日志文件夹不存在")

    def _reload(self):
        config_util = ConfigUtil()
        self.run_util.start_audio_control_threads(config_util)
        self.icon.notify("重新加载成功")
        self.logger.info("Reloaded successfully.")

    def exit_app(self):
        self.logger.info("Exiting StrayUtil.")
        self.icon.stop()
        self.event.set()
