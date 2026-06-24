import datetime
import logging
import subprocess
import time
from typing import Tuple

LOG_NAME = "shell"


def run_shell(command: str) -> Tuple[str, bool]:
    """Executes command and returns content of stdoout and bool as success"""
    logger = logging.getLogger(LOG_NAME)
    start_time = time.time()
    try:
        logger.debug("RUNNING %s", command)
        with subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        ) as proc:
            content = proc.stdout.read().decode("utf-8")
            if error := proc.stderr.read().decode("utf-8"):
                logger.error(error)
            logger.debug(
                "+ ENDED AFTER %s", datetime.timedelta(seconds=time.time() - start_time)
            )
            return content, True
    except Exception as exc:
        logger.error("ERROR: %s", exc)
    return "", False
