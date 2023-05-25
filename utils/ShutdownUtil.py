import time

import win32api
import win32con
import win32gui


class ShutdownUtil:
    def __init__(self, logger):
        self.logger = logger

    def on_win32_wm_event(self, hwnd, msg, w_param, l_param):
        if msg == win32con.WM_QUERYENDSESSION:
            self.logger.info("Received WM_QUERYENDSESSION. Blocking system shutdown.")
            self.logger.info((hwnd, msg, w_param, l_param))
            # 创建阻止关机
            # reason = "Custom reason"
            # ctypes.windll.user32.ShutdownBlockReasonCreate(hwnd, reason)
            # return False
        elif msg == win32con.WM_ENDSESSION:
            self.logger.info("Received WM_ENDSESSION. System is shutting down.")
            self.logger.info("Program will now exit")
        return True

    def create_hidden_window(self):
        h_inst = win32api.GetModuleHandle(None)
        wnd_class = win32gui.WNDCLASS()
        wnd_class.hInstance = h_inst
        wnd_class.lpszClassName = "eventWndClass"
        wnd_class.lpfnWndProc = {
            win32con.WM_QUERYENDSESSION: self.on_win32_wm_event,
            win32con.WM_ENDSESSION: self.on_win32_wm_event
        }

        try:
            hwnd = win32gui.CreateWindowEx(
                win32con.WS_EX_LEFT,
                win32gui.RegisterClass(wnd_class),
                "eventWnd",
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
            return hwnd
        except Exception as e:
            self.logger.error("Exception while creating event window: %s" % str(e))
            return None

    def run(self):
        self.logger.info("Start ShutdownUtil")
        hwnd = self.create_hidden_window()
        if hwnd is None:
            return

        while True:
            win32gui.PumpWaitingMessages()
            time.sleep(1)
