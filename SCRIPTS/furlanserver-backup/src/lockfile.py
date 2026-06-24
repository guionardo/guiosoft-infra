import logging
import datetime
import os
import traceback


class LockError(Exception):
    ...


class Lockfile:
    def __init__(self, filename: str, timeout: datetime.timedelta):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._filename = filename
        self._acquired = False
        self._timeout = timeout

    @property
    def is_locked(self):
        return self._acquired

    def __enter__(self):
        self._acquired = False
        if os.path.isfile(self._filename):
            valid_until = datetime.datetime.now()
            try:
                with open(self._filename) as file:
                    valid_until = datetime.datetime.fromtimestamp(float(file.read()))
            except Exception as exc:
                self.logger.error("Corrupted lock file. %s", exc)

            if valid_until > datetime.datetime.now():
                raise LockError(f"Existent lock until {valid_until}")

        valid_until = datetime.datetime.now() + self._timeout
        try:
            with open(self._filename, "w") as file:
                file.write(str(valid_until.timestamp()))
            self._acquired = True
            self.logger.info("Acquired lock until %s", valid_until)
        except Exception as exc:
            raise LockError() from exc

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            if exc_type == LockError:
                self.logger.error("Failed to acquire lock. %s", exc_val)
            else:
                self.logger.error("Exception during lock context. %s", exc_val)
                self.logger.error("Traceback: %s", traceback.format_tb(exc_tb))
        if self._acquired and os.path.isfile(self._filename):
            self.logger.info("Releasing lock")
            os.remove(self._filename)
        return True
