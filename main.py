import sys
import threading
import time

import pywintypes
import win32api
import win32con
from injector import Injector, singleton

from utils.ConfigUtil import ConfigUtil
from utils.LoggerUtil import LoggerUtil
from utils.PIDLockUtil import PIDLockUtil
from utils.RunUtil import RunUtil
from utils.ShutdownUtil import ShutdownUtil
from utils.StrayUtil import StrayUtil


def configure(binder):
    binder.bind(threading.Event, scope=singleton)


def check_lock():
    cur_lock_util = injector.get(PIDLockUtil)
    if cur_lock_util.is_locked():
        logger.info("Application is already running. Exiting.")
        win32api.MessageBox(0, "请不要重复启动", "后台静音正在运行", win32con.MB_ICONWARNING)
        sys.exit(1)
    else:
        cur_lock_util.create_lock()
    return cur_lock_util


def main():
    stray_util = injector.get(StrayUtil)
    stray_util.run_detached()

    run_util = injector.get(RunUtil)
    run_util.start_audio_control_threads()

    event = injector.get(threading.Event)
    config = injector.get(ConfigUtil).config
    # 这部分会阻塞主进程
    if config["setting"]["bg_run"]:
        if config["setting"]["bg_scan_interval"] is not None:
            run_util.start_background_scanner_thread()
            shutdown_util = injector.get(ShutdownUtil)
            shutdown_util.loop()
        else:
            event.wait()
    else:
        if threading.active_count() < 2:
            logger.info("Target process not found.")
            win32api.MessageBox(0, "请先启动目标进程", "进程未找到", win32con.MB_ICONWARNING)
        while threading.active_count() > 1:
            time.sleep(1)
        else:
            logger.info("Program exits due to the exit of all target processes.")


if __name__ == '__main__':
    injector = Injector(configure)

    logger = injector.get(LoggerUtil).logger
    lock_util = check_lock()

    logger.info("Starting main function.")
    main()

    lock_util.remove_lock()

print(pywintypes)
# pyinstaller -Fw --add-data "resource/;resource/" -i "resource/mute.ico" -n background_muter.v0.2.0.exe main.py
