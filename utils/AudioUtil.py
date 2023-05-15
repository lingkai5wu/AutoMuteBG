import sys
import threading
import time

from pycaw.utils import AudioSession, AudioUtilities

from utils.ProcessUtil import ProcessUtil


def get_all_audio_sessions():
    sessions = AudioUtilities.GetAllSessions()
    res = [session for session in sessions if session.Process is not None]
    return res


# 两个缓动公式
# Source: https://blog.csdn.net/songche123/article/details/102520760
def ease_in_cubic(t, b, c, d):
    t /= d
    return c * t * t * t + b


def ease_out_cubic(t, b, c, d):
    t = t / d - 1
    return c * (t * t * t + 1) + b


class AudioUtil:
    # 循环时间间隔，秒
    LOOP_INTERVAL = 0.2
    # 后台音量，0~1
    BG_VOLUME = 0
    # 淡入淡出
    USE_EASING = True
    EASING_TIME = 0.5
    EASING_STEPS = 50

    def __init__(self, session: AudioSession):
        self.last_target_volume = None
        self.last_volume = None
        self.session = session
        self.process_util = ProcessUtil(session.Process)
        self.easing_thread = None
        self.easing_event = threading.Event()

    def set_volume(self, volume: float):
        def no_easing(cur_volume=volume):
            self.session.SimpleAudioVolume.SetMasterVolume(cur_volume, None)
            self.last_volume = cur_volume

        def easing():
            f = ease_in_cubic if self.last_volume < volume else ease_out_cubic
            c = volume - self.last_volume
            this_last_volume = self.last_volume
            for i in range(self.EASING_STEPS):
                if self.easing_event.isSet():
                    break
                cur_volume = f(i + 1, this_last_volume, c, self.EASING_STEPS)
                # print("sep:{:}, {:.2f} -> {:.2f}".format(i, self.last_volume, cur_volume))
                no_easing(cur_volume)
                time.sleep(self.EASING_TIME / self.EASING_STEPS)

        def stop_easing():
            if self.easing_thread is not None and self.easing_thread.is_alive():
                self.easing_event.set()
                self.easing_thread.join()
                self.easing_event.clear()

        if self.last_target_volume != volume:
            self.last_target_volume = volume
            if not self.USE_EASING or self.last_volume is None:
                no_easing()
            else:
                stop_easing()
                self.easing_thread = threading.Thread(target=easing)
                self.easing_thread.start()

    def main_loop(self, event: threading.Event):
        if not self.process_util.hwnd_list:
            sys.exit()
        while not event.isSet() and self.process_util.is_running():
            if self.process_util.is_window_in_foreground():
                self.set_volume(1)
            else:
                self.set_volume(self.BG_VOLUME)
            time.sleep(self.LOOP_INTERVAL)
        else:
            self.set_volume(1)
            self.easing_thread.join()
