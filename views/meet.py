import datetime

from slack_sdk.models.blocks import InputBlock, SectionBlock, DatePickerElement, TimePickerElement, \
    UserMultiSelectElement, PlainTextInputElement, StaticSelectElement, Option, ChannelSelectElement, \
    ConversationSelectElement, ActionsBlock, CheckboxesElement, ConfirmObject, ExternalDataMultiSelectElement
from slack_sdk.models.views import View

from utils.slack_help import set_time_zone


def create_meet_view(
        time_zone: str = 'Asia/Omsk',
        users: bool = True,
        channel: bool = False,
        init_user: list = None
) -> View:
    now = set_time_zone(datetime.datetime.now(), time_zone)

    time_options = [
          Option(
              text=f'{x} минут',
              value=str(x)
          ) for x in [15, 30, 45, 60]
    ]

    blocks = [
        InputBlock(
            label='Название встречи',
            block_id='title',
            element=PlainTextInputElement(
                initial_value='My Meet'
            )
        ),
        InputBlock(
            label='Гости',
            block_id='users',
            element=UserMultiSelectElement(),
            optional=not users
        ),
        SectionBlock(
            text='Дата встречи',
            block_id='date1:date',
            accessory=DatePickerElement(
                action_id='stub:1',
                initial_date=now.strftime('%Y-%m-%d')
            )
        ),
        SectionBlock(
            text='Начало',
            block_id='date1:time',
            accessory=TimePickerElement(
                action_id='stub:2',
                initial_time=now.strftime('%H:%M')
            )
        ),
        SectionBlock(
            text='Длительность',
            block_id='date2',
            accessory=StaticSelectElement(
                action_id='stub:3',
                initial_option=time_options[0],
                options=[
                    *time_options
                ]
            )
        ),
        InputBlock(
            label='Описание',
            block_id='description',
            element=PlainTextInputElement(
                multiline=True,
            ),
            optional=True
        )
    ]

    if channel:
        options = [
            Option(
                text='Отправить оповещение о встрече в каналы',
                value='true'
            )
        ]

        blocks = blocks[:-1] + [
            ActionsBlock(
                block_id='send_alert',
                elements=[
                    CheckboxesElement(
                        action_id='stub',
                        options=options,
                        initial_options=options
                    )
                ]
            ),
            InputBlock(
                label='Канал',
                block_id='channel',
                element=ConversationSelectElement(
                    default_to_current_conversation=True,
                    response_url_enabled=True
                ),
            )
        ] + blocks[-1:]

    if init_user:
        blocks[1].element.initial_users = init_user

    return View(
        type='modal',
        title='Создание встречи',
        blocks=blocks,
        submit='Отправить',
        close='Закрыть',
        callback_id='meet_view'
    )