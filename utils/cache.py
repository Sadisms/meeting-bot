import datetime
import hashlib
import json
import pickle
import bot

cache = {}


async def compute_key(function, args, kw):
    key = pickle.dumps((function.__name__, args, kw))
    return hashlib.sha1(key).hexdigest()


def memoize(type_storage='mem', ttl=None):
    def wrap(function):
        async def _memoize(*args, **kw):
            key = await compute_key(function, args, kw)

            if type_storage == 'mem':
                if key in cache:
                    if cache[key].get('date_end'):
                        if cache[key]['date_end'] > datetime.datetime.now():
                            return cache[key]['value']
                    else:
                        return cache[key]['value']

            elif type_storage == 'redis':
                if key.encode() in bot.redis_conn.keys():
                    value = json.loads(bot.redis_conn.get(key))
                    if value.get('date_end'):
                        if pickle.loads(value['date_end']) > datetime.datetime.now():
                            return pickle.loads(value['value'])
                        else:
                            bot.redis_conn.delete(key)

                    else:
                        return pickle.loads(value['value'])

            result = await function(*args, **kw)

            if result:
                if type_storage == 'mem':
                    cache[key] = {
                        'value': result,
                    }

                    if ttl:
                        cache[key]['date_end'] = datetime.datetime.now() + datetime.timedelta(seconds=ttl)

                elif type_storage == 'redis':
                    bot.redis_conn.set(key, pickle.dumps(result))

            return result

        return _memoize

    return wrap
