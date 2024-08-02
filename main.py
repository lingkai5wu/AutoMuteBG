import sys
import threading
'''
import psutil
import os
'''
import pywintypes
import win32api
import win32con
from injector import Injector, singleton

from utils.LoggerUtil import LoggerUtil
from utils.PIDLockUtil import PIDLockUtil
from utils.ShutdownUtil import ShutdownUtil
from utils.StrayUtil import StrayUtil
from utils.ThreadUtil import ThreadUtil


def configure(binder):
    binder.bind(threading.Event, scope=singleton)


def check_lock():
    cur_lock_util = injector.get(PIDLockUtil)
    if cur_lock_util.is_locked():
        logger.info("Application is already running.")
        # response = win32api.MessageBox(0, "检测到应用程序已在运行。是否强制启动并退出其他实例？", "后台静音正在运行", win32con.MB_ICONWARNING | win32con.MB_YESNO)
        response = win32api.MessageBox(0, "检测到锁定文件，是否仍然启动（多个进程可能导致问题）？", "后台静音正在运行", win32con.MB_ICONWARNING | win32con.MB_YESNO)
        if response == win32con.IDYES:
            logger.info("User chose to force start. Exiting other instance.")
            cur_lock_util.remove_lock()
            
            ''' 直接杀之前记录的pid可能会杀错，所以先注释掉
            # 遍历进程，中断除自己以外的同名进程
            current_process_id = os.getpid()  # 获取当前进程ID
            for proc in psutil.process_iter(attrs=['pid', 'name']):
                # 检查进程名称是否为background_muter，且进程ID不是当前进程ID
                if proc.info['name'] == 'background_muter.exe' and proc.info['pid'] != current_process_id:
                    proc.terminate()  # 终止该进程
            '''
            cur_lock_util.create_lock()
        else:
            logger.info("User chose not to force start. Exiting.")
            sys.exit(1)
    else:
        cur_lock_util.create_lock()
    return cur_lock_util


def main():
    stray_util = injector.get(StrayUtil)
    stray_util.run_detached()

    thread_util = injector.get(ThreadUtil)
    threading.Thread(
        target=thread_util.background_scanner,
        name="BGScannerThread",
        daemon=True
    ).start()

    shutdown_util = injector.get(ShutdownUtil)
    shutdown_util.loop()


if __name__ == '__main__':
    injector = Injector(configure)

    logger = injector.get(LoggerUtil).logger
    lock_util = check_lock()

    logger.info("Starting main function.")
    main()

    lock_util.remove_lock()

# 打包用
print(pywintypes)
# pyinstaller -Fw --add-data "resource/;resource/" -i "resource/mute.ico" -n background_muter.exe main.py
