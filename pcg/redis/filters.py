import mmh3
import redis


class RedisSetFilter:
    """Trivial redis based filter, utilize set datatype to store values

    This could be used to filter relatively small amount of values.
    The max number of members in a redis set is 232 - 1
    (4294967295, more than 4 billion of members per set).

    Useful to filter urls already crawled, request parameters etc
    """
    __slots__ = [
        '__db',
        'name'
    ]

    @property
    def db(self) -> redis.client.Redis:
        return self.__db

    def __init__(self, name: str, r: redis.client.Redis):
        """RedisSetFilter

        :param name: filter name
        :param r: redis client instance
        """
        self.__db = r
        self.name = name

    def to_set(self) -> set:
        """Return redis set as python set object

        Redis store stings as raw data, and we need decode them back
        https://stackoverflow.com/q/10599147/1376206
        :returns: set -- set of items in redis structure
        """
        return set([x.decode('utf-8') for x in self.db.smembers(self.name)])

    def add(self, *values: str) -> int:
        """Add value or values into the filter

        :param values: one or more values to add
        :returns: int -- number of elements added
        """
        return self.db.sadd(self.name, *values)

    def remove(self, value: str) -> bool:
        """Remove specified value from set

        :param value: delete this value from set
        :returns: bool -- true if element deleted
        """
        return bool(self.db.srem(self.name, value))

    def exists(self, value: str) -> bool:
        """Check if element exists

        :param value: check if value present in set
        :returns: bool -- true if exists
        """
        return bool(self.db.sismember(self.name, value))

    def sizeof(self) -> int:
        """Size of data structure in redis

        :returns: int -- memory used in bytes
        """
        return self.db.memory_usage(self.name, samples=0)

    def __len__(self) -> int:
        """Len of set stored in redis

        :returns: int -- number of elements in set
        """
        return self.db.scard(self.name)

    def __str__(self) -> str:
        """String representation of object

        :returns: str -- class, key name and Redis connection
        """
        return '<RedisSetFilter name={} <{}>>'.format(self.name, self.db)


class RedisBucketFilter:
    """Redis filter with buckets to filter huge volumes of data when just one
    key isn't enoughr. limitation of set data strucure in redis about 4 bil.

    Bucket number calculated as first `bucket_digits` from murmur3 hash

    >> mmh3.hash('B10E7oDEO6-', signed=False).to_bytes(
    >>           4, byteorder='big').hex()
    """

    __slots__ = [
        '__db',
        'name',
        'bucket_digits'
    ]

    @property
    def db(self):
        return self.__db

    def __init__(self, name: str, r: redis.client.Redis,
                 bucket_digits: int = 3):
        """RedisSetFilter

        :param name: filter name
        :param r: redis client instance
        :param bucket_digits: number of digits to cut from mmr3 hash, so with 1
        number of buckets would be 10, with 2 - 100, with 3 - 1000 etc,
        default 3
        """
        self.__db = r
        self.name = name
        self.bucket_digits = bucket_digits

    def _build_key(self, value: str) -> str:
        """Calculate redis key (with bucket) according to value

        :param value: value to add into the bucket
        :returns: str -- full redis key with bucket number assigned
        """
        bucket = str(mmh3.hash(value, signed=False))[:self.bucket_digits]
        return '{}:{}'.format(self.name, bucket)

    def get_bucket(self, value: str) -> str:
        """Calculate bucket number from value

        :param value: value
        :returns: str -- bucket number as string
        """
        return str(mmh3.hash(value, signed=False))[:self.bucket_digits]

    def info(self) -> dict:
        """Information about buckets and number of elements in them.

        :returns: dict in form of {'bucket_name': bucket_len}"""
        bs = {}
        keys = self.db.keys(self.name + ':*')
        for key in keys:
            bs[key.decode('utf-8')] = self.db.scard(key)
        return bs

    def exists(self, value: str) -> bool:
        """Check if element exists

        :param value: check if value present in bucket
        :returns: bool -- true if exists
        """
        k = self._build_key(value)
        return bool(self.db.sismember(k, value))

    def add(self, *values: str) -> int:
        """Add value or values into the filter

        :param values: one or more values to add
        :returns: int -- number of elements added
        """
        result = 0
        for val in values:
            key = self._build_key(val)
            result += self.db.sadd(key, val)
        return result

    def remove(self, value: str) -> int:
        """Remove specified value from bucket

        :param value: delete this value from bucket
        :returns: bool -- true if element deleted
        """
        key = self._build_key(value)
        return bool(self.db.srem(key, value))

    def sizeof(self) -> int:
        """Size of data structure in redis, calculate for all buckets

        :returns: int -- memory used in bytes
        """
        result = 0
        keys = self.db.keys(self.name + ':*')
        for key in keys:
            result += self.db.memory_usage(key, samples=0)
        return result

    def __len__(self) -> int:
        """Number of elements inside all buckets

        :returns: int -- number of elements in buckets
        """
        counter = 0
        keys = self.db.keys(self.name + ':*')
        for key in keys:
            counter += self.db.scard(key)
        return counter

    def __str__(self) -> str:
        """String representation of object

        :returns: str -- class, key name and Redis connection
        """
        return '<RedisBucketFilter name={} <{}>>'.format(self.name, self.db)
