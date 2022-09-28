import peewee

from .base import BaseModel


class OAuthModel(BaseModel):
    id = peewee.PrimaryKeyField()
    user_id = peewee.CharField()
    state = peewee.CharField(null=True)
    slack_token = peewee.TextField(null=True)

    class Meta:
        db_table = 'oauth_cache'
