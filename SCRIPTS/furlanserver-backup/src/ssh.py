import dataclasses
import datetime
import logging
import time
from typing import List

from src.byte_str import parse_bytes
from src.shell import run_shell

LOG_NAME = __name__.split('.')[-1]


@dataclasses.dataclass
class RSyncResult:
    source_folder: str
    files: List[str]
    deleted_files: List[str]
    bytes_sent: int
    bytes_received: int
    bytes_total: int
    bytes_per_second: float
    speed_up: float
    elapsed_time: float

    def log(self, logger: logging.Logger):
        for file in self.files:
            logger.info('✅ %s', file)
        for file in self.deleted_files:
            logger.info('❌ %s', file)

        logger.info(
            'Removed Files: %s - Bytes - Sent: %s | Received: %s | Total: %s',
            len(self.deleted_files),
            self.bytes_sent,
            self.bytes_received,
            self.bytes_total,
        )
        logger.info(
            '%s @ %s', self.source_folder, datetime.timedelta(seconds=self.elapsed_time)
        )


def check_ssh(user: str, host: str) -> bool:
    logger = logging.getLogger(LOG_NAME)
    logger.info('Checking SSH %s@%s', user, host)
    content, ok = run_shell(f'ssh {user}@{host} uptime -p')
    if content.startswith('up '):
        logger.info('Host uptime: %s', content.replace('\n', ''))
        return True

    logger.warning('Host connection %s', content)

    return False


def get_disk_free(user: str, host: str, folder: str):
    """
    ❯ ssh guionardo@192.168.88.35 df /mnt/sdb1
    Sist. Arq.     Blocos de 1K     Usado Disponível Uso% Montado em
    /dev/sdb1         960302096 669780504  241667168  74% /mnt/sdb1
    """
    logger = logging.getLogger(LOG_NAME)
    content, ok = run_shell(f'ssh {user}@{host} df {folder} -h')
    if ok:
        dev, total, used, free, pct, mount = content.splitlines(keepends=False)[
            -1
        ].split()
        logger.info(
            'Disk usage %s:%s %s (%s) %s/%s (%s)',
            host,
            folder,
            mount,
            dev,
            used,
            total,
            pct,
        )
    else:
        logger.warning('ERROR READING DISK USAGE: %s:%s', host, folder)


def get_disk_usage(user: str, host: str, folder: str):
    """
    du -s -h ~/dev
    """
    logger = logging.getLogger(LOG_NAME)
    logger.info('Checking disk usage %s:%s', host, folder)
    content, ok = run_shell(f'ssh {user}@{host} du -s -h "{folder}"')
    if ok:
        logger.info('Disk usage: %s:%s = %s', host, folder, content.replace('\n', ''))
    else:
        logger.warning(f'ERROR READING DISK USAGE: {folder}')


def sync_folder(
    user: str, host: str, source_folder: str, destiny_folder: str
) -> RSyncResult | None:
    """
    rsync -avzh --delete --progress "$ORIGIN/$f" $DESTINY:${SUBFOLDER}$HOSTNAME/${DIA}
    """
    logger = logging.getLogger(LOG_NAME)

    content, ok = run_shell(f'ssh {user}@{host} mkdir -p "{destiny_folder}"')
    if not ok:
        return
    start_time = time.time()
    content, ok = run_shell(
        f'rsync -avzh --delete "{source_folder}" {host}:{destiny_folder}'
    )

    if not ok:
        return

    result = parse_rsync_console(content, time.time() - start_time, destiny_folder)
    logger.debug('%s', result)
    result.log(logger)

    return result


def parse_rsync_console(
    content: str, elapsed_time: float, source_folder: str
) -> RSyncResult:
    files = []
    deleted_files = []
    sent, received, bps, total, spu, deleted = '', '', '', '', '', ''
    for line in content.splitlines(keepends=False):
        line = line.strip()
        if line.startswith('sending incremental file list') or not line:
            continue
        if line.startswith('sent ') and ' received ' in line:
            _, sent, _, _, received, _, bps, _ = line.split(maxsplit=8)
            continue
        if line.startswith('total') and ' speedup is ' in line:
            _, _, _, total, _, _, spu = line.split(maxsplit=7)
            continue
        if line.startswith('deleting '):
            deleted = line.split(maxsplit=2)[1]
            deleted_files.append(deleted)
            continue

        files.append(line)

    return RSyncResult(
        files=files,
        deleted_files=deleted_files,
        bytes_sent=int(parse_bytes(sent)),
        bytes_received=int(parse_bytes(received)),
        bytes_total=int(parse_bytes(total)),
        bytes_per_second=parse_bytes(bps),
        speed_up=float(parse_bytes(spu)),
        elapsed_time=elapsed_time,
        source_folder=source_folder,
    )
