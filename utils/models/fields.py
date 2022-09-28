import base64
import pickle

import jsonpickle
import peewee


class CredentialsField(peewee.Field):  # noqa
    field_type = 'bytea'

    def db_value(self, value):
        if value:
            return base64.b64encode(jsonpickle.encode(value).encode())

    def python_value(self, value):
        if value:
            try:
                return jsonpickle.decode(
                    base64.b64decode(value).decode())
            except ValueError:
                return pickle.loads(base64.b64decode(value))
