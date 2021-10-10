"""Base class and mixins to build App instance"""
# pylint: disable=import-outside-toplevel,no-self-use
# pylint: disable=too-few-public-methods
import uuid
import logging
import functools
import logging.config
from typing import Dict, Optional

import yaml

try:
    import redis
except ImportError:
    # skip import error if redis-py not installed
    pass

try:
    import pymongo
except ImportError:
    # skip import error is pymongo not installed
    pass


from pcg.patterns import Singleton


logger = logging.getLogger("pcg.app")


class AppLoggerFilter(logging.Filter):
    """Add contextual information to the loggers"""

    app_uuid: Optional[uuid.UUID] = None

    def __init__(self, app_uuid=None):
        super().__init__()
        self.app_uuid = app_uuid

    def filter(self, record):
        record.app_uuid = self.app_uuid
        return True


class App(metaclass=Singleton):
    """Store application configuration, provides basic methods"""

    __config: Dict = {}
    __app_uuid: Optional[uuid.UUID] = None

    @property
    def config(self):
        """Return applicaiton config"""
        return self.__config

    @property
    def app_uuid(self):
        """Return uuid for this app"""
        return self.__app_uuid

    @classmethod
    def from_config(cls, config_path: str) -> "App":
        """Create app intance, load config from yaml file"""
        return cls(cls.load_config(config_path))

    def __init__(self, config: Optional[Dict] = None):
        if config is None:
            self.__config = {}
            logger.warning("Config is empty!")
        else:
            self.__config = config

        self.__app_uuid = uuid.uuid1()  # uuid for current app

    @staticmethod
    def load_config(fpath: str) -> Dict:
        """Load config from yaml file"""
        config = None
        with open(fpath) as config_file:
            config = yaml.load(config_file, Loader=yaml.FullLoader)
        assert isinstance(config, dict)
        return config

    def setup_logging(self, verbose=False):
        """Setup application logging"""
        logging.config.dictConfig(self.config["logging"])
        app_logger_filter = AppLoggerFilter(app_uuid=self.app_uuid)
        for handler in logging.root.handlers:
            handler.addFilter(app_logger_filter)

        if verbose:
            logging.basicConfig(level=logging.DEBUG)


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

    def check_mongo_availability(self, uri: str):
        """Check if mongodb available"""


class AppRedisMixin:
    """Add redis database connection"""

    @staticmethod
    def get_redis_pool(uri) -> redis.client.Redis:
        """Return redis client"""
        pool = redis.ConnectionPool.from_url(uri)
        return redis.Redis(connection_pool=pool)
