import threading

from utils.ThreadUtil import background_scanner, start_audio_control_threads


class RunUtil:
    def __init__(self, config_util, event, logger):
        self.config_util = config_util
        self.event = event
        self.logger = logger

    def start_audio_control_threads(self, config_util=None):
        if config_util is not None:
            self.config_util = config_util
        start_audio_control_threads(self.config_util, self.event, self.logger)

    def start_background_scanner_thread(self):
        bg_scan_interval = self.config_util.config["setting"]["bg_scan_interval"]
        background_scanner_thread = threading.Thread(
            target=background_scanner,
            args=(self, bg_scan_interval, self.logger),
            name="BackgroundScannerProcess",
            daemon=True
        )
        background_scanner_thread.start()
