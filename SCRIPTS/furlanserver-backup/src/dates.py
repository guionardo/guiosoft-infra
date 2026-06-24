import os
import datetime


def backup_day_folder(
    base_folder: str, base_date: datetime.datetime = datetime.datetime.now()
):
    """Returns path in {base_folder}/YYYYMMDD"""
    return os.path.join(base_folder, base_date.strftime('%Y%m%d'))


def is_backup_day_folder(folder: str):
    """Returns True if folder is in pattern of backup_day_folder"""
    return len(''.join([c for c in os.path.basename(folder) if '0' <= c <= '9'])) == 8
