import asyncio

import sentry_sdk
import events, middlewares  # noqa
from bot import start_bot
from data.config import SENTRY_TOKEN

sentry_sdk.init(
    SENTRY_TOKEN,
    traces_sample_rate=1.0,
)


def start_manager():
    asyncio.run(start_bot())


if __name__ == "__main__":
    start_manager()