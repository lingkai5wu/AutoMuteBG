import threading

from utils.AudioUtil import get_all_audio_sessions, AudioUtil

TARGET_PROCESS_NAME_LIST = [
    "StarRail.exe"
]
DEBUG = True
if __name__ == '__main__':
    event = threading.Event()
    for session in get_all_audio_sessions():
        if DEBUG or session.Process.name() in TARGET_PROCESS_NAME_LIST:
            threading.Thread(target=AudioUtil(session).main_loop, args=(event,)).start()
    while input() in ("exit", "q"):
        event.set()
        exit()
