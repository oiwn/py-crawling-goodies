"""Mixins for app"""
# pylint: disable=import-outside-toplevel,no-self-use
import functools
from typing import TYPE_CHECKING

import redis
import pymongo

# make linter happy, can't finde attribute "errors" in pymongo
if TYPE_CHECKING:
    from pymongo.errors import ConnectionFailure


class AppMongoMixin:
    """Add connection to mongodb"""

    @functools.lru_cache()
    def get_mongo_client(self, uri: str) -> pymongo.mongo_client.MongoClient:
        """Return mongodb client"""
        return pymongo.MongoClient(uri, connect=False)

    @functools.lru_cache()
    def get_mongo_db(self, uri: str) -> pymongo.database.Database:
        """Return mongodb database object"""
        return self.get_mongo_client(uri).get_database()

    def check_mongo_availability(self, uri: str) -> bool:
        """Check if mongodb available"""
        mongo_client = self.get_mongo_client(uri)
        try:
            # The ismaster command is cheap and does not require auth.
            mongo_client.admin.command("ismaster")
        except pymongo.errors.ConnectionFailure:
            return False
        return True


class AppRedisMixin:
    """Add redis database connection"""

    @staticmethod
    def get_redis_pool(uri) -> redis.client.Redis:
        """Return redis client"""
        pool = redis.ConnectionPool.from_url(uri)
        return pool

    def check_redis_availability(self, uri: str) -> bool:
        """Check if redis server is available"""
        redis_client = redis.from_url(uri)
        if redis_client.ping():
            return True
        return False
