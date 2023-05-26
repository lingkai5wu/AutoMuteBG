import os
import threading
import webbrowser

import pkg_resources
import pystray
from PIL import Image
from injector import singleton, inject

from utils.AudioUtil import get_all_audio_sessions
from utils.ConfigUtil import ConfigUtil
from utils.LoggerUtil import LoggerUtil


def _open_site():
    webbrowser.open('https://gitee.com/lingkai5wu/AutoMuteBG')


@singleton
class StrayUtil:
    @inject
    def __init__(self, config_util: ConfigUtil, logger_util: LoggerUtil, event: threading.Event):
        self.setup_msg = config_util.config["setting"]["setup_msg"]
        self.logger = logger_util.logger
        self.event = event

        name = "后台静音"
        menu = pystray.Menu(
            pystray.MenuItem("开源地址", _open_site),
            pystray.MenuItem("进程列表", self._save_process_list_to_txt),
            pystray.MenuItem("退出", self.exit_app)
        )
        icon = Image.open(pkg_resources.resource_filename(__name__, "../resource/mute.ico"))

        self.icon = pystray.Icon(name, icon, name, menu)

    def run_detached(self):
        def on_icon_ready(icon):
            icon.visible = True
            if self.setup_msg:
                icon.notify("程序启动成功，在系统托盘右键菜单中退出")
            threading.current_thread().setName("StrayRunCallbackThread")
            self.logger.info("Stray is running.")

        self.logger.info("Starting stray.")
        threading.Thread(target=self.icon.run, args=(on_icon_ready,), name="StrayThread").start()

    def _save_process_list_to_txt(self):
        filename = "process_name.txt"
        sessions = get_all_audio_sessions()
        with open(filename, 'w', encoding="utf-8") as file:
            if sessions:
                file.write("当前在音量合成器中注册的进程：\n")
            else:
                file.write("当前在音量合成器中没有进程，请先启动任意进程并播放声音。")
            for session in sessions:
                process_name = session.Process.name()
                file.write(f"{process_name}\n")
        self.logger.info(f"Process list saved to {filename}.")
        os.startfile(filename)

    def exit_app(self):
        self.logger.info("Exiting by StrayUtil.")
        self.event.set()
        self.icon.stop()
