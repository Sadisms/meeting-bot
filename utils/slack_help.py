import datetime
import re
import os
from typing import Union
from zoneinfo import ZoneInfo
from threading import Thread

import dateparser
import pytimeparse
from pyngrok import ngrok
from slack_sdk.models.blocks import SectionBlock

from data.config import MAX_LEN_SECTION_TEXT
from utils.cache import memoize


@memoize()
async def _get_user_info(client, user_id):
    return (await client.users_info(user=user_id)).data['user']


async def get_user_email(client, user_id):
    user = await _get_user_info(client, user_id)
    return user['profile']['email']


async def user_not_bot(client, user_id):
    user = await _get_user_info(client, user_id)
    return not user['is_bot']


def get_str_date(date, time_zone) -> str:
    return date.replace(tzinfo=ZoneInfo(time_zone)).isoformat()


def parse_args_command(text: str = '', time_zone: str = 'Asia/Omsk') -> dict:
    # TODO: Доделать парсинг

    args = {
        'date1': datetime.datetime.now(),
        'date2': (datetime.datetime.now() +
                  datetime.timedelta(minutes=15)),
    }

    parse_args = re.split(r' at ', text)
    args['title'] = parse_args[0] or 'Meet'

    parse_args = re.split(r' for ', parse_args[-1])
    if date1 := dateparser.parse(
            parse_args[0], languages=['en', 'ru'],
            settings={'PREFER_DATES_FROM': 'future'}
    ):
        if date1 > args['date1']:
            if date1.hour == 0:
                date1 = date1.replace(hour=10)

            args['date1'] = date1

    if parse_args.__len__() > 1:
        if ':' in parse_args[1]:
            if date2 := dateparser.parse(
                    parse_args[1], languages=['en', 'ru'],
                    settings={'PREFER_DATES_FROM': 'future'}
            ):
                if date2 > args['date1']:
                    args['date2'] = date2

        else:
            if date2 := pytimeparse.parse(
                    parse_args[1]
            ):
                args['date2'] = args['date1'] + datetime.timedelta(seconds=date2)

    elif date1:
        args['date2'] = (args['date1'] + datetime.timedelta(minutes=15))

    args['date1'] = get_str_date(args['date1'], time_zone)
    args['date2'] = get_str_date(args['date2'], time_zone)

    return args


async def get_user_tz(client, user_id):
    user = (await client.users_info(user=user_id)).data['user']
    return user.get('tz', 'Asia/Omsk')


def parse_datetime(datetime_text: str) -> datetime.datetime:
    if datetime_text:
        return dateparser.parse(datetime_text, languages=['en', 'ru'])


def get_like_data_str(date: datetime) -> str:
    return date.strftime("%d %B %Y, %H:%M")


def get_duration(
        date1: Union[str, datetime.datetime],
        date2: Union[str, datetime.datetime]
):
    if isinstance(date1, str):
        date1 = parse_datetime(date1)

    if isinstance(date2, str):
        date2 = parse_datetime(date2)

    return td_format(date1 - date2)


async def get_data_from_blocks(blocks: dict, skip=None) -> (dict, bool):
    """ Распаривает данные блоков """

    if skip is None:
        skip = []

    data = {}
    empty_data = False
    for block in list(blocks.keys()):
        for el in list(blocks[block].keys()):
            item = blocks[block][el]

            if item['type'] == 'external_select' or item['type'] == 'static_select':
                if item['selected_option']:
                    data[block] = item['selected_option']['value']
                else:
                    if block not in skip:
                        empty_data = True
                    data[block] = None

            elif item['type'] == 'plain_text_input':
                if not item['value']:
                    if block not in skip:
                        empty_data = True
                data[block] = item['value']

            elif item['type'] == 'checkboxes':
                if item['selected_options']:
                    data[block] = [x['value'] for x in item['selected_options']]
                else:
                    if block not in skip:
                        empty_data = True
                    data[block] = None

            elif item['type'] == 'datepicker':
                if not item['selected_date']:
                    if block not in skip:
                        empty_data = True
                else:
                    data[block] = item['selected_date'].replace('-', '.')

            elif item['type'] == 'radio_buttons':
                if not item['selected_option']:
                    if block not in skip:
                        empty_data = True
                else:
                    data[block] = item['selected_option']['value']

            elif item['type'] == 'multi_users_select':
                data[block] = item['selected_users']

            elif item['type'] == 'timepicker':
                data[block] = item['selected_time']

    return data, empty_data


def parse_date_and_time(date, time, time_zone):
    return get_str_date(dateparser.parse(date) + datetime.timedelta(seconds=pytimeparse.parse(time)), time_zone)


def td_format(td_object: datetime.timedelta) -> str:
    seconds = int(td_object.total_seconds())
    periods = [
        ('year',        60*60*24*365),
        ('month',       60*60*24*30),
        ('day',         60*60*24),
        ('hour',        60*60),
        ('minute',      60),
        ('second',      1)
    ]

    strings=[]
    for period_name, period_seconds in periods:
        if seconds > period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            has_s = 's' if period_value > 1 else ''
            strings.append("%s %s%s" % (period_value, period_name, has_s))

    return ", ".join(strings)


def split_text_section(text: str) -> list[SectionBlock]:
    blocks = []
    if text.__len__() > MAX_LEN_SECTION_TEXT:
        text_block = ''
        for x in text.split('\n'):
            if (text_block + '\n' + x).__len__() > MAX_LEN_SECTION_TEXT:
                blocks.append(
                    SectionBlock(
                        text=text_block
                    )
                )
                text_block = ''
            else:
                text_block += x + '\n'

        if text_block:
            blocks.append(
                SectionBlock(
                    text=text_block
                )
            )
    else:
        blocks.append(
            SectionBlock(
                text=text
            )
        )

    return blocks


class ThreadWithResult(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None):
        def function():
            self.result = target(*args, **kwargs)
        super().__init__(group=group, target=function, name=name, daemon=daemon)


def run_with_ngrok(func, port, protocol='http', region='us', save_url=None, kwargs=None):
    print(os.environ['NGROK_AUTH_TOKEN'])
    ngrok.set_auth_token(os.environ['NGROK_AUTH_TOKEN'])
    thread = ThreadWithResult(target=ngrok.connect, args=(port, protocol), kwargs={'region': region})
    thread.start()
    thread.join()

    print(thread.result)
    if save_url:
        with open(save_url, 'w') as f:
            f.write(thread.result.public_url + '/\n')

    func(**(kwargs or {}))
