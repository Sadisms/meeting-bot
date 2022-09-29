from flask import Flask, request, redirect
from slack_bolt.app.async_app import AsyncApp

from api.google_api import GoogleService
from blocks.meet import help_message_block
from data.config import FLASK_SECRET_KEY, OAUTH_URL
from utils.dbworker import get_user_for_state, set_user_credentials, delete_redirect_uri
from utils.slack_help import run_with_ngrok

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY


@app.route('/oauth2callback')
async def hello_world():
    if user := await get_user_for_state(request.args.get('state')):
        service = GoogleService()
        service.creds.redirect_uri = OAUTH_URL()
        service.auth(request.url.replace('http', 'https'))

        await set_user_credentials(user.user_id, service.creds.credentials)
        await delete_redirect_uri(user.user_id)

        app_slack = AsyncApp(token=user.slack_token)
        await app_slack.client.chat_postMessage(
            channel=user.user_id,
            blocks=help_message_block()
        )

    return redirect('slack://')


if __name__ == "__main__":
    run_with_ngrok(app.run, 5000, region='eu', save_url='etc/oauth-server')
