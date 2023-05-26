import os
import tempfile

import psutil
from injector import singleton, inject

from utils.LoggerUtil import LoggerUtil


@singleton
class PIDLockUtil:
    @inject
    def __init__(self, logger_util: LoggerUtil):
        self.logger = logger_util.logger

        self.lockfile = os.path.join(tempfile.gettempdir(), "run.lock")

    def is_locked(self):
        if os.path.isfile(self.lockfile):
            with open(self.lockfile, 'r') as f:
                pid = f.read().strip()
                if pid:
                    return psutil.pid_exists(int(pid))
        return False

    def create_lock(self):
        with open(self.lockfile, 'w') as f:
            f.write(str(os.getpid()))
        self.logger.info("Lock file created.")

    def remove_lock(self):
        if os.path.isfile(self.lockfile):
            os.remove(self.lockfile)
            self.logger.info("Lock file removed.")
