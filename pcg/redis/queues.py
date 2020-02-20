from typing import List

import redis
from pcg.common import ItemSerializer


class RedisJsonLIFOQueue:
    """Simple Queue with Redis Backend
    """

    __slots__ = [
        '__db',
        '__serializer',
        'name',
    ]

    @property
    def db(self) -> redis.client.Redis:
        return self.__db

    @property
    def serializer(self) -> ItemSerializer:
        """Current serializer

        :returns: ItemSerializer -- current serializer instance
        """
        return self.__serializer

    def __init__(self, name: str, r: redis.client.Redis,
                 serializer: str = 'json'):
        """Trivial LIFO redis queue implementation,
        store data as serialized json

        :param name: queue name
        :param r: redis client instance
        :serializer str: string representation of json library
        """
        self.__db = r
        self.__serializer = ItemSerializer(serializer)
        self.name = name

    def is_empty(self) -> bool:
        """Check if queue is empty

        :returns bool: True if empty and False if not
        """
        return len(self) == 0

    def exists(self, name: str) -> bool:
        """Check if queue key exist exists

        :param value: check if value present in set
        :returns: bool -- true if exists
        """
        return bool(self.db.exists(name))

    def put(self, item: dict) -> int:
        """Put item into the queue.

        :param item: serializable item to push into the queue
        :returns: int -- the length of the list after the push operation
        """
        return self.db.rpush(self.name, self.serializer.dumps(item))

    def put_bulk(self, items: List[dict]) -> bool:
        """Use redis pipelines to push bulk into the queue
        :param items: list of serializables to push into the queue
        :returns: bool - if return fit number of items in queue
        """
        pipe = self.db.pipeline()
        for item in items:
            pipe.rpush(self.name, self.serializer.dumps(item))
        res = pipe.execute()
        # last result contains len of queue after operations
        return res[-1] == self.__len__()

    def get(self) -> dict:
        """Pop first element from the list
        :returns: dict - serialized item
        """
        item = self.db.lpop(self.name)
        if item is None:
            return None
        return self.serializer.loads(item)

    def get_block(self, timeout=None) -> dict:
        """Pop item from the queue.

        If optional args block is true and timeout is None (the default), block
        if necessary until an item is available."""
        item = self.db.blpop(self.name, timeout=timeout)

        # return self.serializer.loads(item)
        if item:
            return self.serializer.loads(item[1])
        return None

    def get_bulk(self, number_of_items) -> List[dict]:
        """Remove and return part of list from queue
        """
        items_list = []
        for num in range(number_of_items):
            item = self.db.lpop(self.name)

            if item:
                items_list.append(self.serializer.loads(item))
            else:
                break
        return items_list

    def sizeof(self) -> int:
        """Size of data structure in redis

        :returns: int -- memory used in bytes
        """
        return self.db.memory_usage(self.name, samples=0)

    def __len__(self) -> int:
        """Queue length.

        :returns: int -- number of elements in queue
        """
        return self.db.llen(self.name)

    def __str__(self) -> str:
        """String representation of object

        :returns: str -- class, key name and Redis connection
        """
        return '<RedisJsonLIFOQueue name={} <{}>>'.format(self.name, self.db)
