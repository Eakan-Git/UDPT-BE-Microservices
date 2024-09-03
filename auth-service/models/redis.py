import os
from dotenv import load_dotenv
import redis
import config

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_PORT = os.getenv("REDIS_PORT")

redis = redis.Redis(
    host=REDIS_URL,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    ssl=True,
    decode_responses=True
)

def get_redis_value(key: str):
    return redis.get(key)

def set_redis(key, value):
    return redis.set(key, value, ex=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60, nx=True)

def delete_redis(key):
    return redis.delete(key)