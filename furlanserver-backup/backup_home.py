#!/bin/python3
"""
Run backup to ssh folder
"""

import datetime
import logging
import os
import sys
import traceback

from src.config import get_config
from src.lockfile import LockError, Lockfile
from src.logger import setup_logger
from src.ssh import check_ssh, get_disk_free
from src.sync import delete_old_backups, run_sync
from src.wait_uptime import wait_until_uptime


def main():
    setup_logger()
    logger = logging.getLogger('main')
    try:
        with Lockfile(__file__ + '.lck', datetime.timedelta(minutes=15)):
            wait_until_uptime()
            cfg = None
            try:
                cfg_file = os.path.join(os.path.dirname(__file__), 'backup_home.json')
                if len(sys.argv) > 1:
                    cfg_file = sys.argv[1]

                cfg = get_config(cfg_file)
                if check_ssh(cfg.host_user, cfg.host_name):
                    get_disk_free(cfg.host_user, cfg.host_name, cfg.destiny_folder)
                    delete_old_backups(cfg)
                    run_sync(cfg)

            finally:
                del cfg
    except LockError as exc:
        logger.error(str(exc))
    except Exception as exc:
        if logger.level == logging.DEBUG:
            exc_info = traceback.format_exc()
            logger.error(exc_info)
        else:
            logger.error(str(exc))


if __name__ == '__main__':
    main()
