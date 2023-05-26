from typing import List

import win32gui
import win32process
from psutil import Process


class ProcessUtil:
    def __init__(self, process: Process):
        self.process = process
        self.hwnd_list = self.get_process_hwnd_list()

    def is_running(self):
        return self.process.is_running()

    def is_window_in_foreground(self):
        return win32gui.GetForegroundWindow() in self.hwnd_list

    def get_process_hwnd_list(self):
        def callback(hwnd, res: List):
            _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
            if window_pid == self.process.pid:
                res.append(hwnd)

        hwnd_list = []
        win32gui.EnumWindows(callback, hwnd_list)

        return hwnd_list
