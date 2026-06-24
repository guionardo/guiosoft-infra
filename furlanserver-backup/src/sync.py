from src.config import BkpConfig
from src.ssh import sync_folder
from src.shell import run_shell
from src.dates import backup_day_folder, is_backup_day_folder

import logging
import os
import datetime
from src.pre_run_script import PreRunScript

LOG_NAME = __name__.split('.')[-1]


def run_sync(config: BkpConfig):
    logger = logging.getLogger(LOG_NAME)
    destiny_folder = backup_day_folder(config.destiny_folder)

    pre_run_scripts = [
        PreRunScript(script) for script in config.pre_run_scripts or [] if script
    ]
    for psc in pre_run_scripts:
        psc.command = psc.command.replace('$DESTINY_FOLDER', destiny_folder)
        cmd = f'ssh {config.host_user}@{config.host_name} {psc.command}'
        content, ok = run_shell(cmd)
        if ok:
            logger.info('[%s] = %s', psc.label, content)
        else:
            logger.warning('[%s] %s FAILED', psc.label, psc.command)

    sync_folders = {}
    if config.parsed_other_files:
        sync_folders['others/'] = (
            config.tmp_dir.name + '/',
            os.path.join(destiny_folder, 'others/'),
        )

    for other_folder in config.other_folders:
        _d = f"{destiny_folder}/other_folders/{os.path.basename(other_folder.removesuffix('/'))}"
        sync_folders[other_folder] = (
            other_folder,
            _d,
        )

    home = os.path.expandvars('$HOME/')
    elapsed_time, deleted_files, files = 0, 0, 0
    for source_folder in config.source_folders:
        destiny_path = source_folder.removeprefix(home)
        sync_folders[destiny_path] = (source_folder, destiny_folder)

    for destiny_path, (source_folder, new_destiny_folder) in sync_folders.items():
        logger.info(
            'Syncing %s -> %s',
            source_folder,
            os.path.join(destiny_folder, destiny_path),
        )
        result = sync_folder(
            config.host_user, config.host_name, source_folder, new_destiny_folder
        )
        if result:
            elapsed_time += result.elapsed_time
            deleted_files += len(result.deleted_files)
            files += len(result.files)

    logger.info(
        '* FINISH @ %s - Files: %s - Deleted Files: %s',
        datetime.timedelta(seconds=elapsed_time),
        files,
        deleted_files,
    )


def delete_old_backups(config: BkpConfig):
    logger = logging.getLogger(LOG_NAME)
    content, _ = run_shell(
        f'ssh {config.host_user}@{config.host_name} ls -x -1 "{config.destiny_folder}"'
    )
    backup_days = [
        line
        for line in content.splitlines(keepends=False)
        if line and is_backup_day_folder(line)
    ]
    if len(backup_days) <= config.max_backup_count:
        logger.info('No need to delete old backups: %s', backup_days)
        return
    to_delete = sorted(backup_days)[: len(backup_days) - config.max_backup_count]
    logger.info('To delete old backups: %s', to_delete)
    to_delete = ' '.join([f'{config.destiny_folder}/{f}' for f in to_delete])

    content, _ = run_shell(
        f'ssh {config.host_user}@{config.host_name} rm -r {to_delete}'
    )
    logger.info(f'rm -r {to_delete}')
    logger.info(f'> {content}')
