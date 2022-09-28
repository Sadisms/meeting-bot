import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


formatter = logging.Formatter('%(filename)-15s %(name)-8s LINE:%(lineno)-4d '
                              f'%(levelname)-8s [%(asctime)s] > %(message)s')


def create_logger(name, logger='', path=f"logs", level=logging.INFO, console=True):
    Path(path).mkdir(parents=True, exist_ok=True)

    handler = logging.handlers.TimedRotatingFileHandler(
        filename=f'{path}\\{name}.log', when='W0'
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger(logger)
    logger.setLevel(level)

    logger.addHandler(handler)

    if console:
        console_out = logging.StreamHandler()
        console_out.setFormatter(formatter)
        logger.addHandler(console_out)

    return logger


create_logger('slack_bolt', 'slack_bolt.AsyncApp')
slack_logging = create_logger('support_log', 'support')
