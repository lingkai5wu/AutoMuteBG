import win32gui
import win32process
import psutil
from pycaw.utils import AudioUtilities

def get_all_audio_sessions():
    sessions = AudioUtilities.GetAllSessions()
    res = [session for session in sessions if session.Process is not None]
    return res

def get_all_window_processes():
    window_processes = []
    ignore_list = ['TextInputHost.exe']  # 添加过滤列表

    def enum_window_callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                p = psutil.Process(pid)
                process_name = p.name()
                if process_name not in ignore_list:
                    window_title = win32gui.GetWindowText(hwnd)
                    window_processes.append((process_name, window_title))
            except psutil.NoSuchProcess:
                pass

    win32gui.EnumWindows(enum_window_callback, None)
    return window_processes
