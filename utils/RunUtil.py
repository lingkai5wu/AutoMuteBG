import threading

from injector import Injector, singleton, inject

from utils.ConfigUtil import ConfigUtil
from utils.LoggerUtil import LoggerUtil
from utils.ThreadUtil import background_scanner, start_audio_control_threads


@singleton
class RunUtil:
    @inject
    def __init__(self, injector: Injector, config_util: ConfigUtil,
                 event: threading.Event, logger_util: LoggerUtil):
        self.injector = injector

        self.config_util = config_util
        self.event = event
        self.logger = logger_util.logger

    def start_audio_control_threads(self, config_util=None):
        if config_util is not None:
            self.config_util = config_util
        start_audio_control_threads(self.injector)

    def start_background_scanner_thread(self):
        background_scanner_thread = threading.Thread(
            target=background_scanner,
            args=(self.injector, self),
            name="BackgroundScannerProcess",
            daemon=True
        )
        background_scanner_thread.start()
