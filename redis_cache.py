import redis
import json
import pickle

class RedisCache:
    def __init__(self, host='redis', port=6379):
        self.redis_client = redis.StrictRedis(host=host, port=port)
        # self.ttl = ttl

    def set(self, key, value, ttl = 600):
        """
        Зберігає значення в Redis з вказаним ключем.
        :param key: ключ
        :param value: значення
        """
        object = pickle.dumps(value)
        self.redis_client.set(key, object, ex=ttl)

    def get(self, key):
        """
        Отримує значення з Redis за вказаним ключем.
        :param key: ключ
        :return: значення або None, якщо ключ не знайдено
        """
        value = self.redis_client.get(key)        
        if value is not None:
            res = pickle.loads(value)
            return res
        else:
            return None

    def delete(self, key):
        """
        Видаляє значення з Redis за вказаним ключем.
        :param key: ключ
        """
        self.redis_client.delete(key)
