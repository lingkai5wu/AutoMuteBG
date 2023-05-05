import concurrent
import threading
from concurrent.futures import ThreadPoolExecutor

import win32api

from utils.AudioUtil import get_all_audio_sessions, AudioUtil
from utils.StrayUtil import StrayUtil

TARGET_PROCESS_NAME_LIST = [
    "StarRail.exe"
]
DEBUG = True
if __name__ == '__main__':
    event = threading.Event()
    futures = []
    for session in get_all_audio_sessions():
        if DEBUG or session.Process.name() in TARGET_PROCESS_NAME_LIST:
            futures.append(
                ThreadPoolExecutor().submit(AudioUtil(session).main_loop, event)
            )
    if futures:
        stray_util = StrayUtil()
        stray_util.run_app(event)
        concurrent.futures.wait(futures)
        stray_util.exit_app()
    else:
        win32api.MessageBox(0, "请先启动对应进程", "进程未找到", win32con.MB_ICONWARNING)

# pyinstaller -Fw --add-data "resource/mute.ico;resource" -i "resource/mute.ico" -n background_muter.v0.1.2.exe main.py
