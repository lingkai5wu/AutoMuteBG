import threading
import time

from utils.AudioUtil import get_all_audio_sessions, AudioUtil


def start_audio_control_threads(config_util, event, logger):
    alive_process = [process.name for process in threading.enumerate() if process.is_alive()]
    # logger.info(alive_process)
    for session in get_all_audio_sessions():
        process_name = session.Process.name()
        if process_name in config_util.config["processes"] and process_name not in alive_process:
            logger.info(f"Starting audio control thread for process: {process_name}")
            audio_util = AudioUtil(session, config_util, event, logger)
            thread = threading.Thread(target=audio_util.loop, name=process_name)
            thread.start()


def background_scanner(run_util, bg_scan_interval, logger):
    logger.info(f"Starting with scan interval: {bg_scan_interval}s")
    while True:
        run_util.start_audio_control_threads()
        time.sleep(bg_scan_interval)
