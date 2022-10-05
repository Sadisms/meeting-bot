import pytest

from utils.slack_help import parse_args_command


class TestCommand:
    def test_parse_command(self):
        DATA = [
            {
                'text': 'Test Demo at 13:00 for 13:40',
                'result': {
                    'date1': '2022-10-05T13:00:00+06:00',
                    'date2': '2022-10-05T13:40:00+06:00',
                    'title': 'Test Demo'
                }
            },
        ]

        for x in DATA:
            assert parse_args_command(x['text']) == x['result']

