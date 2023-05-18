import concurrent
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

import win32api
import win32con

from utils.AudioUtil import get_all_audio_sessions, AudioUtil
from utils.ConfigUtil import ConfigUtil
from utils.PIDLockUtil import PIDLockUtil
from utils.StrayUtil import StrayUtil


def check_lock():
    lock_util = PIDLockUtil()
    if lock_util.is_locked():
        win32api.MessageBox(0, "请不要重复启动", "后台静音正在运行", win32con.MB_ICONWARNING)
        sys.exit(1)
    else:
        lock_util.create_lock()


def main():
    config_util = ConfigUtil()
    event = threading.Event()
    futures = []
    for session in get_all_audio_sessions():
        if session.Process.name() in config_util.config["processes"]:
            futures.append(
                ThreadPoolExecutor().submit(AudioUtil(session, config_util).main_loop, event)
            )
    if futures:
        stray_util = StrayUtil()
        stray_util.run_app(event)
        concurrent.futures.wait(futures)
        stray_util.exit_app()
    else:
        win32api.MessageBox(0, "请先启动目标进程", "进程未找到", win32con.MB_ICONWARNING)


if __name__ == '__main__':
    check_lock()
    main()

# import pywintypes
# pyinstaller -Fw --add-data "resource/;resource/" -i "resource/mute.ico" -n background_muter.v0.1.7.exe main.py
