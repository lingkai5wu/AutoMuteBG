import threading
import time

from comtypes import CoInitialize
from injector import Injector, singleton, inject

from utils.AudioUtil import get_all_audio_sessions, AudioUtil
from utils.ConfigUtil import ConfigUtil
from utils.LoggerUtil import LoggerUtil


@singleton
class ThreadUtil:
    @inject
    def __init__(self, injector: Injector, config_util: ConfigUtil,
                 event: threading.Event, logger_util: LoggerUtil):
        self.injector = injector
        self.config_util = config_util
        self.event = event
        self.logger = logger_util.logger

    def start_audio_control_threads(self):
        alive_process = [process.name for process in threading.enumerate() if process.is_alive()]
        # self.logger.info(alive_process)
        sessions = get_all_audio_sessions()
        for session in sessions:
            process_name = session.Process.name()
            if process_name in self.config_util.config["processes"] and str(session.ProcessId) not in alive_process:
                self.logger.info(f"Found target process: {process_name} (PID: {session.ProcessId})")
                audio_util = AudioUtil(session, self.config_util, self.event, self.logger)
                thread = threading.Thread(target=audio_util.loop, name=session.ProcessId)
                thread.start()

    def background_scanner(self):
        CoInitialize()

        config = self.config_util.config
        bg_scan_interval = config["setting"]["bg_scan_interval"]
        self.logger.info(f"Starting with scan interval: {bg_scan_interval}s")
        while True:
            self.start_audio_control_threads()
            time.sleep(bg_scan_interval)
