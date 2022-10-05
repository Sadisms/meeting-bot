from bot import app
from utils.logging import create_logger


logger = create_logger('slack_request')


@app.middleware
async def log_request(body, next):
    logger.info(body)
    return await next()