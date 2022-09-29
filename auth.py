from bot import app
from utils.slack_help import run_with_ngrok

run_with_ngrok(app.start, 3000, region='ap', save_url='etc/auth-bot')
