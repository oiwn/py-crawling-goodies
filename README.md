# py-crawling-goodies

[![codecov](https://codecov.io/gh/istinspring/py-crawling-goodies/branch/master/graph/badge.svg)](https://codecov.io/gh/istinspring/py-crawling-goodies)


Helpers and stuff for building web crawlers.


## Redis

- `RedisSetFilter` filter based on redis set.
- `RedisBucketFilter` filter which 'shard' values over few sets.


### RedisSetFilter

```python
import redis
from pcg.redis.filters import RedisSetFilter

db = redis.from_url('redis://localhost:6379/15')
f = RedisSetFilter('pcg:set-filter', r=db)

# adding elements to filter
f.add('bob')
f.add('alice', 'jane')

# delete element
f.remove('jane')

if f.exists('alice'):
    print('Alice already there!')

if not f.exists('jane'):
    print('Jane not yet come!')
```
