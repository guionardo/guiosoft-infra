import logging
import time
from datetime import timedelta
from subprocess import getstatusoutput


def wait_until_uptime(
    min_uptime: timedelta = timedelta(minutes=1), get_status_output=getstatusoutput
):
    status, output = get_status_output("uptime -p")
    logger = logging.getLogger("uptime")
    if status > 0:
        logger.warning(
            "Failed to run uptime (status=%d) [%s], waiting for %s",
            status,
            output,
            min_uptime,
        )
        time.sleep(min_uptime.total_seconds())
        return

    # up 2 days, 2 hours, 4 minutes
    value = None
    d, h, m = 0, 0, 0
    for word in output.replace(",", "").split():
        if word.isnumeric():
            value = int(word)
        elif word.startswith("day") and value is not None:
            d = value
            value = None
        elif word.startswith("hour") and value is not None:
            h = value
            value = None
        elif word.startswith("minute") and value is not None:
            m = value
            value = None

    uptime = timedelta(days=d, minutes=m, hours=h)
    if uptime > min_uptime:
        logger.info("System uptime %s", uptime)
        return
    wait = min_uptime - uptime
    logger.warning("Waiting for %s until uptime is %s", wait, min_uptime)
    time.sleep(wait.total_seconds())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    wait_until_uptime()
