from slack_sdk.models.blocks import ActionsBlock, SectionBlock, ButtonElement, DividerBlock

from data.config import MAX_LEN_SECTION_TEXT
from utils.slack_help import split_text_section


def call_block(
        user_id: str,
        url: str,
        title: str,
        start: str,
        duration: str,
        description: str = '',
        users=None
):
    if users is None:
        users = []

    blocks = [
        SectionBlock(
            text=f"<@{user_id}> created a meeting{(' with ' + ', '.join(f'<@{x}>' for x in users)) if users else '.'}\n"
                 f"Title: *{title}*\n"
                 f"Will Start at: *{start}*\n"
                 f"For: *{duration}*"
        ),
        ActionsBlock(
            elements=[
                ButtonElement(
                    action_id='stub',
                    text='Join to meeting',
                    url=url,
                    style='primary'
                )
            ]
        )
    ]

    if description:
        description_text = '\n'.join(
            [f">{x}" for x in description.split('\n')]
        )
        description_header = 'Description: \n'

        if blocks[0].text.text.__len__() + (description_header + description_text).__len__() > MAX_LEN_SECTION_TEXT:
            description_blocks = split_text_section(
                text='\n'.join(
                    [f">{x}" for x in description.split('\n')]
                )
            )
            description_blocks[0].text.text = 'Description: \n' + description_blocks[0].text.text
            blocks = blocks[:1] + description_blocks + blocks[1:]
        else:
            blocks[0].text.text += '\n' + description_header + description_text

    return blocks


def auth_block(text, url):
    return [
        SectionBlock(
            text=text
        ),
        ActionsBlock(
            elements=[
                ButtonElement(
                    action_id='delete',
                    text='Connect',
                    style='primary',
                    url=url
                )
            ]
        )
    ]


def help_message_block():
    return [
        SectionBlock(
            text='Hi, I am an application for creating meetings in Google Meet.\n'
                 'You can create meetings in chats or private messages, and if I can, '
                 'I will send an invitation directly to the chat or only to you.\n'
                 'To register an meet in the window send:\n'
                 '> /call modal'
        ),
        DividerBlock(),
        SectionBlock(
            text='By passing the window, you can register team meetings in this format:\n'
                 '> /call [Meet name] at [Start time] for [Duration]'
        ),
        DividerBlock(),
        SectionBlock(
            text='Samples:\n'
                 '> /call My Meet at 10 min for 1 hour\n'
                 '> /call Demo meet at 11:00 for 10 min\n'
                 '> /call Start meet at 13 sep 11:00 for 1h\n'
        )
    ]
