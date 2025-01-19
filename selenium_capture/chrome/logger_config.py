import logging
import colorlog

handler = colorlog.StreamHandler()

formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
)

handler.setFormatter(formatter)

logger = colorlog.getLogger('global')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

logging.getLogger('requests').setLevel(logging.WARNING)