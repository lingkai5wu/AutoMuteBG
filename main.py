import sys
import threading

import win32api
import win32con

from utils.ConfigUtil import ConfigUtil
from utils.PIDLockUtil import PIDLockUtil
from utils.RunUtil import RunUtil
from utils.StrayUtil import StrayUtil
from utils.ThreadUtil import ThreadUtil


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
    thread_util = ThreadUtil()
    run_util = RunUtil(config_util, event, thread_util)
    run_util.start_audio_control_threads()

    stray_util = StrayUtil(run_util)
    stray_util.run_detached(event)

    if config_util.config["setting"]["bg_run"]:
        if config_util.config["setting"]["bg_scan_interval"] is not None:
            run_util.start_background_thread()
        else:
            event.wait()
    else:
        if thread_util.thread_dict:
            thread_util.wait_threads()
        else:
            win32api.MessageBox(0, "请先启动目标进程", "进程未找到", win32con.MB_ICONWARNING)
    stray_util.exit_app()


if __name__ == '__main__':
    check_lock()
    main()

# import pywintypes
# pyinstaller -Fw --add-data "resource/;resource/" -i "resource/mute.ico" -n background_muter.v0.2.0.exe main.py
