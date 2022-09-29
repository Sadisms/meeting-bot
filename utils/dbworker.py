from .models.google_models import UserCredentials
from .models.backend_models import OAuthModel
from .models.base import conn


@conn.atomic()
def init_tables():
    conn.create_tables([UserCredentials, OAuthModel])


@conn.atomic()
async def _get_user_credentials(user_id)-> UserCredentials:
    return UserCredentials.get_or_create(user_id=user_id)[0]


@conn.atomic()
async def set_user_credentials(user_id, credentials):
    user_credentials = await _get_user_credentials(user_id)
    user_credentials.credentials = credentials
    user_credentials.save()


@conn.atomic()
async def get_user_credentials(user_id):
    return (await _get_user_credentials(user_id)).credentials


@conn.atomic()
async def _get_oauth(user_id) -> OAuthModel:
    return OAuthModel.get_or_create(user_id=user_id)[0]


@conn.atomic()
async def create_redirect_uri(user_id, token, state):
    user = await _get_oauth(user_id)
    user.slack_token = token
    user.state = state
    user.save()


@conn.atomic()
async def get_oauth_message(user_id):
    return (await _get_oauth(user_id)).message_ts


@conn.atomic()
async def get_user_for_state(state):
    oauth = OAuthModel.select().where(
        OAuthModel.state == state
    )

    if oauth.count() > 0:
        return oauth.get()


@conn.atomic()
async def delete_redirect_uri(user_id):
    (await _get_oauth(user_id)).delete().execute()
