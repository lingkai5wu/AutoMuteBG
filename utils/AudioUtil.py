import threading
import time

from pycaw.utils import AudioSession

from utils.ConfigUtil import ConfigUtil
from utils.LoggerUtil import LoggerUtil
from utils.ProcessUtil import ProcessUtil

# 两个缓动公式
# Source: https://blog.csdn.net/songche123/article/details/102520760
def _ease_in_cubic(t, b, c, d):
    t /= d
    return c * t * t * t + b


def _ease_out_cubic(t, b, c, d):
    t = t / d - 1
    return c * (t * t * t + 1) + b


class AudioUtil:
    def __init__(self, session: AudioSession, config_util: ConfigUtil,
                 event: threading.Event, logger: LoggerUtil.logger):
        self.session = session
        self.config = config_util.get_by_process(session.Process.name())
        self.event = event
        self.logger = logger

        self.process_util = ProcessUtil(session.Process)
        self.last_target_volume = None
        self.last_volume = None
        self.easing_thread = None
        self.stop_easing_thread = False

        # 运行函数
        self._check_fg_volume()

    def _check_fg_volume(self):
        if self.config["fg_volume"] == "auto":
            self.config["fg_volume"] = self.session.SimpleAudioVolume.GetMasterVolume()
            # 意外退出的情况
            if self.config["fg_volume"] == self.config["bg_volume"]:
                self.config["fg_volume"] = 1
            self.logger.info(f"Change fg_volume to {self.config['fg_volume']}.")

    def set_volume(self, volume: float):
        def no_easing(cur_volume=volume):
            self.session.SimpleAudioVolume.SetMasterVolume(cur_volume, None)
            self.last_volume = cur_volume

        def easing(stop_easing_thread):
            f = _ease_in_cubic if self.last_volume < volume else _ease_out_cubic
            c = volume - self.last_volume
            this_last_volume = self.last_volume
            for i in range(self.config["easing"]["steps"]):
                if stop_easing_thread():
                    break
                cur_volume = f(i + 1, this_last_volume, c, self.config["easing"]["steps"])
                # print("sep:{:}, {:.2f} -> {:.2f}".format(i, self.last_volume, cur_volume))
                no_easing(cur_volume)
                time.sleep(self.config["easing"]["duration"] / self.config["easing"]["steps"])

        def stop_easing():
            if self.easing_thread is not None and self.easing_thread.is_alive():
                self.stop_easing_thread = True
                self.easing_thread.join()
                self.stop_easing_thread = False

        if self.last_target_volume != volume:
            self.last_target_volume = volume
            if self.config["easing"] is None or self.last_volume is None:
                no_easing()
            else:
                stop_easing()
                self.easing_thread = threading.Thread(
                    target=easing,
                    args=(lambda: self.stop_easing_thread,),
                    name="EasingThread",
                    daemon=True
                )
                self.easing_thread.start()

    def loop(self):
        self.logger.info("Starting loop.")
        while not self.event.isSet() and self.process_util.is_running():
            if self.process_util.is_window_in_foreground():
                self.set_volume(self.config["fg_volume"])
            else:
                self.set_volume(self.config["bg_volume"])
            time.sleep(self.config["loop_interval"])
        else:
            self.stop_easing_thread = True
            self.session.SimpleAudioVolume.SetMasterVolume(self.config["fg_volume"], None)
            self.logger.info("Exiting loop.")
