import uuid
from datetime import datetime, timedelta


import google.auth.transport.requests
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from blocks.meet import auth_block
from data.config import GOOGLE_TOKEN_FILE, SCOPES, OAUTH_URL
from utils.dbworker import get_user_credentials, set_user_credentials, create_redirect_uri
from utils.logging import slack_logging

CALENDAR_ID = 'primary'


class GoogleService:
    def __init__(self):
        self.service = None

        if GOOGLE_TOKEN_FILE.exists():
            self.creds = InstalledAppFlow.from_client_secrets_file(GOOGLE_TOKEN_FILE, scopes=SCOPES)
        else:
            raise FileNotFoundError('"token.json" does not exist in project root directory')

        self.calendar_id = CALENDAR_ID

    def auth(self, authorization_response):
        self.creds.fetch_token(authorization_response=authorization_response)

    @staticmethod
    def build_calendar(credentials):
        return build('calendar', 'v3', credentials=credentials)

    @staticmethod
    def _reformat_dates(date1, date2):
        return f'{date1}T00:00:00+06:00', f'{date2}T23:59:00+06:00'

    def create_event(
            self, build,
            title='Meet',
            description='',
            users=None,
            date1=datetime.now().isoformat(),
            date2=(datetime.now() + timedelta(minutes=15)).isoformat(),
    ):
        if users is None:
            users = []

        uid_meet = str(uuid.uuid4())

        body = {
            'start': {'dateTime': date1, 'timeZone': 'Asia/Omsk'},
            'end': {'dateTime': date2, 'timeZone': 'Asia/Omsk'},
            'summary': title,
            'attendees': users,
            'description': description,
            "conferenceData": {
                "createRequest": {
                    "conferenceSolutionKey": {
                        "type": "hangoutsMeet"
                    },
                    "requestId": uid_meet
                }
            },
        }
        new_event = build.events().insert(
            calendarId=self.calendar_id,
            sendUpdates='all',
            body=body,
            conferenceDataVersion=1
        ).execute()
        slack_logging.info(f'Created event {new_event.get("id")} {uid_meet}, {date1} - {date2}')

        return new_event.get('hangoutLink'), uid_meet, new_event.get("id")

    async def get_user_creds(self, user_id, token, respond):
        if creds := await get_user_credentials(user_id):
            if creds.expiry > datetime.utcnow():
                request = google.auth.transport.requests.Request()
                creds.refresh(request)
                await set_user_credentials(user_id, creds)

            return creds

        self.creds.redirect_uri = OAUTH_URL + 'oauth2callback'
        authorization_url, state = self.creds.authorization_url(
            access_type='offline',
        )

        await create_redirect_uri(
            user_id=user_id,
            token=token,
            state=state
        )

        await respond(
            blocks=auth_block(
                text='Please visit this URL to authorize this application',
                url=authorization_url
            )
        )

    def _delete_event(
        self,
        build,
        event_id
    ):
        build.events().delete(
            calendarId=self.calendar_id,
            eventId=event_id
        ).execute()