import peewee
import peewee_async
from data.config import DB_CONFIG

conn = peewee_async.PostgresqlDatabase(**DB_CONFIG, autorollback=True)


class BaseModel(peewee.Model):
    class Meta:
        database = conn
