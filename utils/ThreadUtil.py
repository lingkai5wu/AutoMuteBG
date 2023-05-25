import threading
import time

from utils.AudioUtil import get_all_audio_sessions, AudioUtil


def start_audio_control_threads(config_util, event):
    active_process = [process.name for process in threading.enumerate()]
    for session in get_all_audio_sessions():
        process_name = session.Process.name()
        if process_name in config_util.config["processes"] and process_name not in active_process:
            audio_util = AudioUtil(session, config_util)
            thread = threading.Thread(target=audio_util.loop, args=(event,), name=process_name)
            thread.start()


def bg_run_thread(run_util, bg_scan_interval):
    while not run_util.event.isSet():
        run_util.start_audio_control_threads()
        time.sleep(bg_scan_interval)
