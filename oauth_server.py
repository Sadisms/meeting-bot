from flask import Flask, request, redirect
from slack_bolt.app.async_app import AsyncApp


from api.google_api import GoogleService
from blocks.meet import help_message_block
from data.config import FLASK_SECRET_KEY, OAUTH_URL, SLACK_CONFIG, SLACK_SCOPES
from utils.dbworker import get_user_for_state, set_user_credentials, delete_redirect_uri, set_user_slack_token
from utils.slack_help import run_with_ngrok, slack_oauth_link

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY


@app.route('/oauth2callback/google')
async def oauth_google():
    state = request.args.get('state', '')
    if user := await get_user_for_state(state):
        service = GoogleService()
        service.creds.redirect_uri = OAUTH_URL() + '/google'
        service.auth(request.url.replace('http', 'https'))

        await set_user_credentials(user.user_id, service.creds.credentials)

        url = slack_oauth_link(
            user_scopes=SLACK_SCOPES['user_scopes'],
            state=state
        )

        return redirect(url)

    return """
    <script>
    window.close();
    </script>
    """


@app.route('/oauth2callback/slack')
async def oauth_slack():
    if user := await get_user_for_state(request.args.get('state')):
        slack_app = AsyncApp(token=SLACK_CONFIG['bot_token'])

        response = await slack_app.client.oauth_v2_access(
            code=request.args.get('code'),
            client_secret=SLACK_CONFIG['client_secret'],
            client_id=SLACK_CONFIG['client_id'],
            redirect_uri=OAUTH_URL().replace('http:', 'https:') + '/slack'
        )

        await set_user_slack_token(
            user_id=response['authed_user']['id'],
            token=response['authed_user']['access_token']
        )

        await delete_redirect_uri(user.user_id)

        app_slack = AsyncApp(token=user.slack_token)
        await app_slack.client.chat_postMessage(
            channel=user.user_id,
            blocks=help_message_block()
        )

    return """
        <script>
        window.close();
        </script>
        """


if __name__ == "__main__":
    run_with_ngrok(app.run, 5000, region='eu', save_url='etc/oauth-server')
