import datetime

from slack_sdk.models.blocks import InputBlock, SectionBlock, DatePickerElement, TimePickerElement, \
    UserMultiSelectElement, PlainTextInputElement, StaticSelectElement, Option
from slack_sdk.models.views import View

from utils.slack_help import set_time_zone


def create_meet_view(time_zone: str = 'Asia/Omsk'):
    now = set_time_zone(datetime.datetime.now(), time_zone)

    time_options = [
          Option(
              text=f'{x} mins',
              value=str(x)
          ) for x in [15, 30, 45, 60]
    ]

    return View(
        type='modal',
        title='Create Meet',
        blocks=[
            InputBlock(
                label='Title meet',
                block_id='title',
                element=PlainTextInputElement(
                    initial_value='My Meet'
                )
            ),
            InputBlock(
                label='Pick users from the list',
                block_id='users',
                element=UserMultiSelectElement()
            ),
            SectionBlock(
                text='Pick a date for the meeting',
                block_id='date1:date',
                accessory=DatePickerElement(
                    action_id='stub:1',
                    initial_date=now.strftime('%Y-%m-%d')
                )
            ),
            SectionBlock(
                text='Pick a time for the meeting',
                block_id='date1:time',
                accessory=TimePickerElement(
                    action_id='stub:2',
                    initial_time=now.strftime('%H:%M')
                )
            ),
            SectionBlock(
                text='For how long will meeting last',
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
                label='Description',
                block_id='description',
                element=PlainTextInputElement(
                    multiline=True,
                ),
                optional=True
            )
        ],
        submit='Send',
        close='Close',
        callback_id='meet_view'
    )