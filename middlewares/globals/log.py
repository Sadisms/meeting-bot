from bot import app
from utils.logging import create_logger


logger = create_logger('request', 'slack_request')


@app.middleware
async def log_request(body, next):
    """ Логируем все действия юзера в боте и прописываем для payload новый параметр _user_id
        сформированный из user_id и team_id или enterprise_id,
        последний используется если платная подписка у грида """

    logger.info(body)

    if body.get('event'):
        if body['event'].get('hidden'):
            return await next()

    user_id = body.get('user_id')
    if not user_id:
        if body.get('user'):
            user_id = body['user']['id']
        elif body.get('event'):
            user_id = body['event']['user']

    id_grid = body.get('enterprise_id')
    if not id_grid:
        if body.get('enterprise'):
            id_grid = body['enterprise']['id']

        elif body.get('team_id'):
            id_grid = body['team_id']

        elif body.get('team'):
            id_grid = body['team']['id']

    body['_user_id'] = f"{user_id}_{id_grid}"

    return await next()