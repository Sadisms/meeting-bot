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
            text=f"<@{user_id}> создал встречу {(' для ' + ', '.join(f'<@{x}>' for x in users)) if users else '.'}\n"
                 f"Название встречи: *{title}*\n"
                 f"Начало: *{start}*\n"
                 f"Длительность: *{duration}*"
        ),
        ActionsBlock(
            elements=[
                ButtonElement(
                    action_id='stub',
                    text='Подключиться',
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
        description_header = 'Описание: \n'

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


def auth_block(url):
    return [
        SectionBlock(
            text='Для авторизации в приложении нажми на кнопку'
        ),
        ActionsBlock(
            elements=[
                ButtonElement(
                    action_id='delete',
                    text='Авторизоваться',
                    style='primary',
                    url=url
                )
            ]
        )
    ]


def help_message_block():
    return [
        SectionBlock(
            text='Привет, я приложение для создания встреч в Google Meet.\n'
                 'Вы можете создавать встречи в чатах или личных сообщениях, '
                 'я отправлю приглашение непосредственно в чат или только вам.\n'
                 'Чтобы зарегистрировать встречу в окне отправьте команду:\n'
                 '> /gmeet\n'
                 'Чтобы быстро зарегистрировать встречу, используйте команду:\n'
                 '> /gmeetnow\n'
                 'Вы можете использовать команду в личных сообщениях, тогда ваш оппонент будет '
                 'автоматически приглашен на встречу.\n'
                 ':exclamation: Если вы используете shortcut`ы в треях в приватных каналах для создания собрания, '
                 'то уведомление о собрании придет в трее от вашего имени.\n'
        ),
        DividerBlock(),
        SectionBlock(
            text='Помимо окна, вы можете зарегистрировать встречи команды в этом формате:\n'
                 '> /gmeet [Название встречи] at [Начало] for [Длительность]'
        ),
        DividerBlock(),
        SectionBlock(
            text='Примеры:\n'
                 '> /gmeet My Meet at 10 min for 1 hour\n'
                 '> /gmeet Demo meet at 11:00 for 10 min\n'
                 '> /gmeet Start meet at 13 sep 11:00 for 1h\n'
        )
    ]
