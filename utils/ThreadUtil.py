import threading
import time

from injector import Injector

from utils.AudioUtil import get_all_audio_sessions, AudioUtil
from utils.ConfigUtil import ConfigUtil
from utils.LoggerUtil import LoggerUtil


def start_audio_control_threads(injector: Injector):
    alive_process = [process.name for process in threading.enumerate() if process.is_alive()]
    # logger.info(alive_process)
    for session in get_all_audio_sessions():
        process_name = session.Process.name()
        config_util = injector.get(ConfigUtil)
        logger = injector.get(LoggerUtil).logger
        event = injector.get(threading.Event)
        if process_name in config_util.config["processes"] and process_name not in alive_process:
            logger.info(f"Starting audio control thread for process: {process_name}")
            audio_util = AudioUtil(session, config_util, event, logger)
            thread = threading.Thread(target=audio_util.loop, name=process_name)
            thread.start()


def background_scanner(injector: Injector, run_util):
    logger = injector.get(LoggerUtil).logger
    config = injector.get(ConfigUtil).config
    bg_scan_interval = config["setting"]["bg_scan_interval"]
    logger.info(f"Starting with scan interval: {bg_scan_interval}s")
    while True:
        run_util.start_audio_control_threads()
        time.sleep(bg_scan_interval)
