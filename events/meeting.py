import re
from contextlib import suppress

from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient

from api.google_api import GoogleService
from blocks.meet import call_block, help_message_block
from bot import app
from utils.slack_help import parse_args_command, get_user_tz, get_data_from_blocks, \
    get_user_email, parse_date_and_time, user_not_bot, get_like_data_str, get_duration, parse_datetime, \
    get_time_zone_short_name
from views.meet import create_meet_view


async def send_meet(body, client, respond, say, time_zone, args=None, users=None, thread_ts=''):
    if users is None:
        users = []

    if args is None:
        args = {}

    user_id = body.get('user_id') or body.get('user', {}).get('id')

    google_service = GoogleService()
    if creds := await google_service.get_user_creds(user_id, client.token, respond):
        build = google_service.build_calendar(creds)
        meet_url, *_ = google_service.create_event(
            **args,
            build=build
        )

        block = call_block(
            url=meet_url,
            user_id=user_id,
            title=args.get('title') or 'My Meet',
            start=f"{get_like_data_str(parse_datetime(args.get('date1')))} {get_time_zone_short_name(time_zone)}",
            duration=get_duration(args.get('date2'), args.get('date1')),
            description=args.get('description', ''),
            users=users
        )
        try:
            if thread_ts:
                await client.chat_postMessage(
                    channel=body.get('channel_id') or body.get('channel', {}).get('id'),
                    blocks=block,
                    thread_ts=thread_ts
                )
            else:
                await say(
                    blocks=block
                )

        except:  # noqa
            await client.chat_postMessage(
                channel=user_id,
                blocks=block
            )

        for user in users:
            with suppress(SlackApiError):
                await client.chat_postMessage(
                    channel=user,
                    blocks=block
                )


@app.command('/gmeetnow')
@app.shortcut('create_meet')
async def gmeet_now(ack, say, body, client, respond):
    await ack()

    time_zone = await get_user_tz(client, body.get('user_id') or body['user']['id'])

    await send_meet(
        body=body,
        client=client,
        respond=respond,
        say=say,
        time_zone=time_zone,
        args=parse_args_command(
            time_zone=time_zone
        ),
        thread_ts=body.get('message_ts', '')  # message_ts Будет в случае если был вызван shortcut
    )


@app.command('/gmeet')
async def init_call_command(ack, body, respond, client: AsyncWebClient, say):
    await ack()
    text = body.get('text', '').strip()
    user_id = body['user_id']
    time_zone = await get_user_tz(client, user_id)

    if text.startswith('help'):
        await client.chat_postMessage(
            channel=user_id,
            blocks=help_message_block()
        )

    elif text:
        await send_meet(
            body=body,
            client=client,
            respond=respond,
            say=say,
            time_zone=time_zone,
            args=parse_args_command(
                text=text,
                time_zone=time_zone
            )
        )

    else:
        google_service = GoogleService()
        if await google_service.get_user_creds(user_id, client.token, respond):
            await client.views_open(
                trigger_id=body['trigger_id'],
                view=create_meet_view(time_zone)
            )


@app.view('meet_view')
async def meet_view_send(ack, body, client, say, respond):
    await ack()

    time_zone = await get_user_tz(client, body['user']['id'])

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

    await send_meet(
        body=body,
        client=client,
        respond=respond,
        say=say,
        time_zone=time_zone,
        args=data_from_blocks,
        users=users_ids
    )


@app.action(re.compile("stub"))
async def stub(ack):
    await ack()


@app.action(re.compile("delete"))
async def delete(ack, respond):
    await ack()

    await respond(
        response_type='ephemeral',
        text='',
        replace_original=True,
        delete_original=True
    )
