import sys
import threading
import time

import win32api
import win32con

from utils.ConfigUtil import ConfigUtil
from utils.LoggerUtil import LoggerUtil
from utils.PIDLockUtil import PIDLockUtil
from utils.RunUtil import RunUtil
from utils.ShutdownUtil import ShutdownUtil
from utils.StrayUtil import StrayUtil


def check_lock():
    lock_util = PIDLockUtil(logger)
    if lock_util.is_locked():
        logger.info("Application is already running. Exiting.")
        win32api.MessageBox(0, "请不要重复启动", "后台静音正在运行", win32con.MB_ICONWARNING)
        sys.exit(1)
    else:
        lock_util.create_lock()


def main():
    event = threading.Event()
    run_util = RunUtil(config_util, event, logger)
    run_util.start_audio_control_threads()

    stray_util = StrayUtil(run_util, config_util.config["setting"]["stray_setup_msg"], logger)
    stray_util.run_detached(event)

    if config_util.config["setting"]["bg_run"]:
        if config_util.config["setting"]["bg_scan_interval"] is not None:
            run_util.start_background_thread()
            threading.Thread(target=ShutdownUtil(logger).run)
        else:
            event.wait()
    else:
        while threading.enumerate():
            time.sleep(1)
        else:
            logger.info("Target process not found.")
            win32api.MessageBox(0, "请先启动目标进程", "进程未找到", win32con.MB_ICONWARNING)


if __name__ == '__main__':
    config_util = ConfigUtil()
    logger = LoggerUtil(config_util.config["setting"]["max_log_files"]).logger
    check_lock()
    logger.info("Starting main function.")
    main()
