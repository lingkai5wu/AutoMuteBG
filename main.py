import concurrent
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

import win32api
import win32con

from utils.AudioUtil import get_all_audio_sessions, AudioUtil
from utils.PIDLockUtil import PIDLockUtil
from utils.StrayUtil import StrayUtil

TARGET_PROCESS_NAME_LIST = [
    "StarRail.exe"
]
if __name__ == '__main__':
    lock_util = PIDLockUtil()
    if lock_util.is_locked():
        win32api.MessageBox(0, "请不要重复启动", "正在运行", win32con.MB_ICONWARNING)
        sys.exit(1)
    else:
        lock_util.create_lock()

    event = threading.Event()
    futures = []
    for session in get_all_audio_sessions():
        if session.Process.name() in TARGET_PROCESS_NAME_LIST:
            futures.append(
                ThreadPoolExecutor().submit(AudioUtil(session).main_loop, event)
            )
    if futures:
        stray_util = StrayUtil()
        stray_util.run_app(event)
        concurrent.futures.wait(futures)
        stray_util.exit_app()
    else:
        win32api.MessageBox(0, "请先启动游戏本体", "进程未找到", win32con.MB_ICONWARNING)

# pyinstaller -Fw --add-data "resource/mute.ico;resource" -i "resource/mute.ico" -n background_muter.v0.1.3.exe main.py
