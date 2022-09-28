import peewee

from .base import BaseModel
from .fields import CredentialsField


class UserCredentials(BaseModel):
    id = peewee.PrimaryKeyField()
    user_id = peewee.CharField()
    credentials = CredentialsField(null=True)

    class Meta:
        db_table = 'meet_user_credentials'
