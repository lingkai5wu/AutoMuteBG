import threading

from utils.ThreadUtil import bg_run_thread, start_audio_control_threads


class RunUtil:
    def __init__(self, config_util, event):
        self.config_util = config_util
        self.event = event

    def start_audio_control_threads(self, config_util=None):
        if config_util is not None:
            self.config_util = config_util
        start_audio_control_threads(self.config_util, self.event)

    def start_background_thread(self):
        bg_scan_interval = self.config_util.config["setting"]["bg_scan_interval"]
        thread = threading.Thread(target=bg_run_thread, args=(self, bg_scan_interval))
        thread.start()
