"""Logger configuration."""

import logging

from colorlog import ColoredFormatter


LEVEL = logging.INFO

log = logging.getLogger()
formatter = ColoredFormatter("%(log_color)s%(asctime)s %(levelname)-8s %(message)s",
                             datefmt='%Y-%m-%d %H:%M:%S',
                             reset=True,
                             log_colors={'DEBUG': 'cyan',
                                         'INFO': 'blue',
                                         'WARNING': 'yellow',
                                         'ERROR': 'red',
                                         'CRITICAL': 'red,bg_white'},
                             secondary_log_colors={},
                             style='%')
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
log.addHandler(console_handler)
log.setLevel(LEVEL)
log.info(f'Configured logger. Logging level: {logging.getLevelName(LEVEL)}')
