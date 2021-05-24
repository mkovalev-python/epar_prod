__author__ = 'Rayleigh'
import redis
from tracker import settings

service_queue = redis.StrictRedis(
    host=settings.ORDERS_REDIS_HOST,
    port=settings.ORDERS_REDIS_PORT,
    db=settings.ORDERS_REDIS_DB,
    password=settings.ORDERS_REDIS_PASSWORD
).publish
