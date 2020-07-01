# py-crawling-goodies

[![codecov](https://codecov.io/gh/istinspring/py-crawling-goodies/branch/master/graph/badge.svg)](https://codecov.io/gh/istinspring/py-crawling-goodies)


Helpers and stuff for building web crawlers.

# Installation

```bash

pip install py-crawling-goodies
```


## Redis

- `RedisSetFilter` filter based on redis set.
- `RedisBucketFilter` filter which 'shard' values over few sets.
- `RedisJsonLIFOQueue` LIFO queue based on redis


### RedisSetFilter

Trivial implementation of filter using redis set datatype

```python
import redis
from pcg import RedisSetFilter

db = redis.from_url('redis://localhost:6379/15')
f = RedisSetFilter('pcg:set-filter', r=db)

# adding elements to filter
f.add('bob')
assert f.add('alice', 'jane') == 2

# delete element
f.remove('jane')

if f.exists('alice'):
    print('Alice already there!')

if not f.exists('jane'):
    print('Jane not yet come!')
```

### RedisBucketFilter

Split filter into the buckets, based on murmur hash.

```python
import redis
from pcg import RedisBucketFilter

db = redis.from_url('redis://localhost:6379/15')
f = RedisBucketFilter('pcg:bucket-filter', r=db)

# adding elements to filter
f.add('alice')
assert f.add('bob', 'jane') == 2

# delete element
f.remove('jane')

# what is bucket for bob?
bn = f.get_bucket('bob')
print(bn)

# info about all available buckets
print(f.info())

if f.exists('bob'):
    print('Bob already there!')

if not f.exists('jane'):
    print('Jane not yet come!')
```

### RedisJsonLIFOQueue

Implementation of LIFO queue with json serializable data on top of Redis

```python
import redis
from pcg import RedisJsonLIFOQueue

db = redis.from_url('redis://localhost:6379/15')
q = RedisJsonLIFOQueue('pcg:lifo-queue', r=db)

# check if it's empty
print(q.is_empty())

# put item into queue
q.put({'alice': 1})

# put many items!
items = [{'b': 1}, {'b': 2}, {'b': 3}]
q.put_bulk(items)

# check length
assert len(q) == 2

# get one item
print(q.get())

# get few items
print(q.get_bulk(2))

# check if queue exists and contain something
print(q.exists('pcg:lifo-queue'))
```
