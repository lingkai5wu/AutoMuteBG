import threading
import time

from utils.AudioUtil import get_all_audio_sessions, AudioUtil


def start_audio_control_threads(config_util, event, thread_util):
    for session in get_all_audio_sessions():
        process_name = session.Process.name()
        if process_name in config_util.config["processes"] and not thread_util.is_thread_running(process_name):
            audio_util = AudioUtil(session, config_util)
            thread = threading.Thread(target=audio_util.loop, args=(event, thread_util), name=process_name)
            thread.start()
            thread_util.add_thread(process_name, thread)


def bg_run_thread(run_util, bg_scan_interval):
    while not run_util.event.isSet():
        run_util.start_audio_control_threads()
        time.sleep(bg_scan_interval)


class ThreadUtil:
    def __init__(self):
        self.thread_dict = {}
        self.lock = threading.Lock()

    def add_thread(self, thread_name, thread):
        with self.lock:
            self.thread_dict[thread_name] = thread

    def remove_thread(self, thread_name):
        with self.lock:
            del self.thread_dict[thread_name]

    def wait_threads(self):
        while True:
            with self.lock:
                if not self.thread_dict:
                    break
            time.sleep(0.1)

    def is_thread_running(self, thread_name):
        with self.lock:
            return thread_name in self.thread_dict
