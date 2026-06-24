import dataclasses
import json
import logging
import os
import shutil
import tempfile
from typing import List, Optional

from src.other_files import OtherFile
from src.other_folder import OtherFolder

LOG_NAME = __name__.split('.')[-1]


@dataclasses.dataclass
class BkpConfig:
    source_folders: List[str]
    host_name: str
    host_user: str
    destiny_folder: str
    pre_run_scripts: Optional[List[str]]
    other_files: Optional[List[str]]
    other_folders: Optional[List[str]]
    parsed_other_files: dict = dataclasses.field(init=False)
    tmp_dir: tempfile.TemporaryDirectory = dataclasses.field(init=False)
    max_backup_count: int = dataclasses.field(default=15)

    def __post_init__(self):
        logger = logging.getLogger(LOG_NAME)
        self.tmp_dir = tempfile.TemporaryDirectory(prefix='backup_home')
        logger.debug('Created tmp folder %s', self.tmp_dir.name)
        self.other_files = self.other_files or []
        self.parsed_other_files = {}
        self.parsed_other_folders = {}

        for other_file in self.other_files:
            other = OtherFile(other_file)
            if not other.exists:
                logger.warning('Unexistent other file %s', other_file)
                continue
            tmp_dest_path = os.path.abspath(
                os.path.join(self.tmp_dir.name, f'.{os.path.dirname(other.filename)}')
            )
            os.makedirs(tmp_dest_path, exist_ok=True)
            tmp_dest_file = os.path.join(
                tmp_dest_path, os.path.basename(other.realname)
            )
            shutil.copyfile(other.filename, tmp_dest_file)
            self.parsed_other_files[other.realname] = tmp_dest_file

        for other_folder in self.other_folders:
            other = OtherFolder(other_folder)
            if not other.exists:
                logger.warning('Unexistent other folder %s', other_folder)
                continue
            self.parsed_other_folders[
                os.path.dirname(other.foldername)
            ] = other.foldername

        if not isinstance(self.source_folders, list):
            self.source_folders = [self.source_folders]

        existent = []
        for source_folder in self.source_folders:
            source_folder = os.path.abspath(os.path.expandvars(source_folder))
            if not os.path.exists(source_folder):
                logger.warning('Unexistent source folder %s', source_folder)
            else:
                existent.append(source_folder)
        self.source_folders = existent

        self.pre_run_scripts = [
            script for script in self.pre_run_scripts or [] if script
        ]

    def __del__(self):
        logger = logging.getLogger(LOG_NAME)
        logger.debug('Removing tmp folder %s', self.tmp_dir.name)
        self.tmp_dir.cleanup()


def get_config(filename: str) -> BkpConfig:
    logger = logging.getLogger(LOG_NAME)
    try:
        with open(filename) as file:
            content = json.load(file)
        cfg = BkpConfig(**content)
        logger.debug('configuration: %s', cfg)
        logger.info('configuration loaded from %s', os.path.abspath(filename))
        return cfg
    except Exception as exc:
        logger.error(str(exc))
        raise
