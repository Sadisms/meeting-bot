import re
from contextlib import suppress

import sentry_sdk
from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient

from api.google_api import GoogleService
from blocks.meet import call_block, help_message_block
from bot import app
from utils.dbworker import get_user_slack_token
from utils.slack_help import parse_args_command, get_user_tz, get_data_from_blocks, \
    get_user_email, parse_date_and_time, user_not_bot, get_like_data_str, get_duration, parse_datetime, \
    get_time_zone_short_name, get_users_for_dm
from views.meet import create_meet_view, alert_add_channel_view


async def send_meet(body, client, respond, time_zone, args=None, users=None):
    if users is None:
        users = []

    if args is None:
        args = {}

    user_id = body.get('user_id') or body.get('user', {}).get('id')

    google_service = GoogleService()
    if creds := await google_service.get_user_creds(user_id, client, respond):
        build = google_service.build_calendar(creds)
        meet_url, *_ = google_service.create_event(
            **args,
            build=build,
            user_id=user_id
        )

        return call_block(
            url=meet_url,
            user_id=user_id,
            title=args.get('title') or 'My Meet',
            start=f"{get_like_data_str(parse_datetime(args.get('date1')))} {get_time_zone_short_name(time_zone)}",
            duration=get_duration(args.get('date2'), args.get('date1')),
            description=args.get('description', ''),
            users=users
        )


@app.shortcut('create_meet')
async def gmeet_now(ack, body, client, respond):
    await ack()

    user_id = body['user']['id']
    time_zone = await get_user_tz(client, user_id)
    args = parse_args_command(
        time_zone=time_zone
    )

    if block := await send_meet(
        body=body,
        client=client,
        respond=respond,
        time_zone=time_zone,
        args=args
    ):
        try:
            await client.chat_postMessage(
                channel=body['channel']['id'],
                blocks=block,
                thread_ts=body['message']['ts']
            )
        except SlackApiError as e:
            if e.response['error'] == 'channel_not_found':
                try:
                    await client.chat_postMessage(
                        channel=body['channel']['id'],
                        blocks=block,
                        thread_ts=body['message']['ts'],
                        token=await get_user_slack_token(user_id)
                    )
                    return

                except SlackApiError as e:
                    if e.response['error'] == 'channel_not_found':
                        await client.views_open(
                            view=alert_add_channel_view(),
                            trigger_id=body['trigger_id']
                        )

            sentry_sdk.capture_exception(e)


@app.command('/gmeetnow')
@app.command('/gmeet')
async def init_call_command(ack, body, respond, client: AsyncWebClient):
    await ack()

    text = body.get('text', '').strip() if body['command'] == '/gmeet' else ''

    user_id = body['user_id']
    time_zone = await get_user_tz(client, user_id)
    args = parse_args_command(
        text=text,
        time_zone=time_zone
    )

    kwargs_view = {}
    user_ids = []
    if body['channel_name'] == 'directmessage':
        if users := await get_users_for_dm(
            client=client,
            channel_id=body['channel_id'],
            user_id=user_id
        ):
            for user in users:
                if await user_not_bot(client, user):
                    user_ids.append(user)
                    if args.get("users"):
                        args['users'] += [
                            {'email': await get_user_email(client, user)}
                        ]

                    else:
                        args['users'] = [
                            {'email': await get_user_email(client, user)}
                        ]

            if user_ids:
                kwargs_view = dict(
                    init_user=user_ids[0]
                )

    else:
        kwargs_view = dict(
            users=False,
            channel=True
        )

    if text.startswith('help'):
        await respond(
            blocks=help_message_block()
        )

    elif text or body['command'] == '/gmeetnow':
        if block := await send_meet(
            body=body,
            client=client,
            respond=respond,
            time_zone=time_zone,
            args=args,
            users=user_ids
        ):
            await respond(
                blocks=block,
                response_type='in_channel'
            )

    else:
        google_service = GoogleService()
        if await google_service.get_user_creds(user_id, client, respond):
            await client.views_open(
                trigger_id=body['trigger_id'],
                view=create_meet_view(
                    time_zone=time_zone,
                    **kwargs_view
                )
            )


@app.view('meet_view')
async def meet_view_send(ack, body, client, respond):
    await ack()

    time_zone = await get_user_tz(client, body['user']['id'])
    user_id = body['user']['id']

    data_from_blocks, _ = await get_data_from_blocks(body['view']['state']['values'])

    users = []
    users_ids = []
    for user in data_from_blocks['users']:
        if await user_not_bot(client, user):
            users_ids.append(user)
            users.append({'email': await get_user_email(client, user)})

    data_from_blocks['users'] = users
    data_from_blocks['date1'] = parse_date_and_time(
        date=data_from_blocks.pop('date1:date'),
        time=data_from_blocks.pop('date1:time') + ':00',
        time_zone=time_zone
    )
    data_from_blocks['date2'] = parse_date_and_time(
        date=data_from_blocks['date1'],
        time=data_from_blocks['date2'] + ':00',
        time_zone=time_zone
    )

    if block := await send_meet(
        body=body,
        client=client,
        respond=respond,
        time_zone=time_zone,
        args=data_from_blocks,
        users=users_ids
    ):
        for user in users:
            with suppress(SlackApiError):
                await client.chat_postMessage(
                    channel=user,
                    blocks=block
                )

        if data_from_blocks.get('send_alert') == ['true'] and data_from_blocks.get('channel'):
            await respond(
                blocks=block,
                response_type='in_channel'
            )

        else:
            await client.chat_postMessage(
                channel=user_id,
                blocks=block
            )


@app.action(re.compile("stub"))
async def stub(ack):
    await ack()


@app.action(re.compile("delete"))
async def delete(ack, respond):
    await ack()

    await respond(
        delete_original=True
    )
