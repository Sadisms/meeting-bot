import peewee

from .base import BaseModel
from .fields import CredentialsField


class UserCredentials(BaseModel):
    id = peewee.PrimaryKeyField()
    user_id = peewee.CharField()
    credentials = CredentialsField(null=True)
    slack_token = peewee.CharField()

    class Meta:
        db_table = 'meet_user_credentials'
