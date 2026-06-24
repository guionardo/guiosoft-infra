import logging
import os


def setup_logger():
    if hasattr(logging, '_setup_done'):
        return
    log_level = logging.getLevelName(os.getenv('LOG_LEVEL', 'INFO'))
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(name)-10s %(message)s', level=log_level
    )
    setattr(logging, '_setup_done', True)
