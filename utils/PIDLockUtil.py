import os
import tempfile

import psutil


class PIDLockUtil:
    def __init__(self, logger):
        self.logger = logger
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
