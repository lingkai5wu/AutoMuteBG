import logging
import os
from datetime import datetime

import pkg_resources

LOG_PATH = "../logs/"


class LoggerUtil:
    def __init__(self, max_log_files: int):
        self.log_dir = None
        self.max_log_files = max_log_files

        self.logger = self._setup_logging()
        self._delete_old_log_files()

    def _setup_logging(self):
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(threadName)s - %(message)s")

        # 设置控制台日志输出
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        if self.max_log_files > 0:
            self.log_dir = pkg_resources.resource_filename(__name__, LOG_PATH)
            os.makedirs(self.log_dir, exist_ok=True)
            log_file = os.path.join(self.log_dir, datetime.now().strftime("%Y%m%d%H%M%S") + ".log")
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger

    def _delete_old_log_files(self):
        log_files = [f for f in os.listdir(self.log_dir) if f.endswith(".log")]
        log_files.sort()

        if len(log_files) > self.max_log_files:
            files_to_delete = log_files[:len(log_files) - self.max_log_files]
            for file_name in files_to_delete:
                file_path = os.path.join(self.log_dir, file_name)
                os.remove(file_path)