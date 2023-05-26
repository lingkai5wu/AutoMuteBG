import threading
import time

import win32api
import win32con
import win32gui
from injector import singleton, inject

from utils.LoggerUtil import LoggerUtil
from utils.PIDLockUtil import PIDLockUtil
from utils.StrayUtil import StrayUtil


@singleton
class ShutdownUtil:
    @inject
    def __init__(self, stray_util: StrayUtil, lock_util: PIDLockUtil,
                 event: threading.Event, logger_util: LoggerUtil):
        self.stray_util = stray_util
        self.lock_util = lock_util
        self.event = event
        self.logger = logger_util.logger

        self.hwnd = None

    def on_win32_wm_event(self, h_wnd, u_msg, w_param, l_param):
        self.logger.info(self, h_wnd, u_msg, w_param, l_param)
        if u_msg == win32con.WM_QUERYENDSESSION:
            self.logger.warn(f"Received WM_QUERYENDSESSION. {h_wnd, u_msg, w_param, l_param}")
        elif u_msg == win32con.WM_ENDSESSION:
            self.logger.warn("Received WM_ENDSESSION. System is shutting down.")
            self.stray_util.exit_app()
            self.lock_util.remove_lock()
            while threading.active_count() > 2:
                alive_process = [process.name for process in threading.enumerate() if process.is_alive()]
                self.logger.info(alive_process)
                time.sleep(0.1)
            self.logger.info("Program exit.")
        return True

    def create_hidden_window(self):
        h_inst = win32api.GetModuleHandle(None)
        wnd_class = win32gui.WNDCLASS()
        wnd_class.hInstance = h_inst
        wnd_class.lpszClassName = "AutoMuteBGClass"
        wnd_class.lpfnWndProc = {
            win32con.WM_QUERYENDSESSION: self.on_win32_wm_event,
            win32con.WM_ENDSESSION: self.on_win32_wm_event
        }

        self.hwnd = win32gui.CreateWindowEx(
            win32con.WS_EX_LEFT,
            win32gui.RegisterClass(wnd_class),
            "AutoMuteBG",
            0,
            0,
            0,
            win32con.CW_USEDEFAULT,
            win32con.CW_USEDEFAULT,
            0,
            0,
            h_inst,
            None
        )

    def destroy_hidden_window(self):
        if self.hwnd is not None:
            win32gui.DestroyWindow(self.hwnd)
            win32gui.UnregisterClass("AutoMuteBGClass", win32api.GetModuleHandle(None))

    def loop(self):
        self.logger.info("Start ShutdownUtil")
        try:
            self.create_hidden_window()
            while not self.event.is_set():
                win32gui.PumpWaitingMessages()
                time.sleep(0.5)
            self.destroy_hidden_window()
        except Exception as e:
            self.logger.error(e, exc_info=True, stack_info=True)
