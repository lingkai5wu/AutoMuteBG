import sys
import threading
import time

from pycaw.utils import AudioSession, AudioUtilities

from utils.ProcessUtil import ProcessUtil


def get_all_audio_sessions():
    sessions = AudioUtilities.GetAllSessions()
    res = [session for session in sessions if session.Process is not None]
    return res


class AudioUtil:
    # 循环时间间隔，秒
    LOOP_INTERVAL = 0.2
    # 后台音量，0~1
    BG_VOLUME = 0

    def __init__(self, session: AudioSession):
        self.last_volume = None
        self.session = session
        self.process_util = ProcessUtil(session.Process)

    def set_volume(self, volume: float):
        if self.last_volume != volume:
            self.session.SimpleAudioVolume.SetMasterVolume(volume, None)
            print(self.session.Process.name(), self.last_volume, volume, sep='\t')
            self.last_volume = volume

    def main_loop(self, event: threading.Event):
        if not self.process_util.hwnd_list:
            sys.exit()
        volume_status = 0
        while not event.isSet() and self.process_util.is_running():
            if self.process_util.is_window_in_foreground():
                if volume_status == 0:
                    # 声音渐强，每次增加0.1，0.5s完成
                    for volume in range(0, 11):
                        self.set_volume(volume / 10)
                        time.sleep(0.05)
                    volume_status = 1
            else:
                self.set_volume(self.BG_VOLUME)
                volume_status = 0
            time.sleep(self.LOOP_INTERVAL)
        else:
            self.set_volume(1)
