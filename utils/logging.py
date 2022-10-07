import logging

from logstash_async.handler import AsynchronousLogstashHandler
from logstash_async.formatter import LogstashFormatter

from data.config import DEBUG, ELK_CONFIG

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


logstash_handler = AsynchronousLogstashHandler(ELK_CONFIG['host'], int(ELK_CONFIG['port']), database_path=None)
logstash_handler.setFormatter(
    LogstashFormatter(
        message_type=f"{ELK_CONFIG['prefix']}",
        extra_prefix=f"{ELK_CONFIG['prefix']}"
    )
)
root = logging.getLogger('')
root.setLevel(logging.INFO)
root.addHandler(logstash_handler)

create_logger('slack_bolt.AsyncApp')
slack_logging = create_logger('meeting')
