from pathlib import Path

from environs import Env

env = Env()
env.read_env(path='.env_meeting')

DEBUG = env.bool('DEBUG', False)

BASE_DIR = Path(__file__).resolve().parent.parent
GOOGLE_TOKEN_FILE = BASE_DIR / 'token.json'
SCOPES = [
    'https://www.googleapis.com/auth/calendar'
]
SENTRY_TOKEN = env.str("sentry_token")

NGROK_TOKEN = env.str("NGROK_TOKEN")

FLASK_SECRET_KEY = env.str('FLASK_SECRET_KEY')

MAX_LEN_SECTION_TEXT = 2999  # 3000

SLACK_CONFIG = {
    'bot_token': env.str('BOT_TOKEN'),
    'app_token': env.str('APP_TOKEN'),
    'client_id': env.str('CLIENT_ID'),
    'client_secret': env.str('CLIENT_SECRET'),
    'signing_secret': env.str('SIGNING_SECRET')
}

SLACK_SCOPES = {
    'user_scopes': ['im:read', 'mpim:read', 'channels:read', 'groups:read', 'chat:write'],
    'bot_scopes': ['chat:write', 'chat:write.public', 'commands', 'groups:history',
                'groups:read', 'groups:write',
                'im:read', 'im:write', 'im:history', 'mpim:write', 'users:read', 'users:read.email',
                'users.profile:read', 'team:read']
}

DB_CONFIG = {
    'database': env.str('DB_NAME'),
    'host': env.str('DB_HOST', 'localhost'),
    'user': env.str('DB_USER'),
    'password': env.str('DB_PASS'),
}

ELK_CONFIG = {
    'host': env.str('ELK_HOST'),
    'port': env.str('ELK_PORT'),
    'prefix': env.str('ELK_PREFIX')
}

def OAUTH_URL():
    with open('etc/oauth-server', 'r') as f:
        return f.read()
