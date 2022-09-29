import logging

from data.config import DEBUG

formatter = logging.Formatter('%(filename)-15s %(name)-8s LINE:%(lineno)-4d '
                              f'%(levelname)-8s [%(asctime)s] > %(message)s')


def create_logger(logger='', level=logging.INFO, console=True):
    logger = logging.getLogger(logger)
    logger.setLevel(level if not DEBUG else logging.DEBUG)

    if console:
        console_out = logging.StreamHandler()
        console_out.setFormatter(formatter)
        logger.addHandler(console_out)

    return logger


create_logger('slack_bolt.AsyncApp')
slack_logging = create_logger('meeting')
