from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.oauth.async_oauth_flow import AsyncOAuthFlow

from data.config import SLACK_CONFIG, SLACK_SCOPES
from utils.logging import slack_logging

app = AsyncApp(
    signing_secret=SLACK_CONFIG['signing_secret'],
    oauth_flow=AsyncOAuthFlow.sqlite3(
        database='._.db',
        client_id=SLACK_CONFIG['client_id'],
        client_secret=SLACK_CONFIG['client_secret'],
        scopes=SLACK_SCOPES['bot_scopes'],
        user_scopes=SLACK_SCOPES['user_scopes']
    )
)


async def start_bot():
    slack_logging.info('Start bot')
    await AsyncSocketModeHandler(app, SLACK_CONFIG['app_token']).start_async()
