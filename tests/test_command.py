import pytest

from utils.slack_help import parse_args_command


class TestCommand:
    def test_parse_command(self):
        DATA = [
            {
                'text': 'Test Demo at 13:00 for 14h',
                'result': []
            },
        ]

        for x in DATA:
            print(parse_args_command(x['text']))

