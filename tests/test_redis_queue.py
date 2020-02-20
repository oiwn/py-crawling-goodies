import redis
import pytest

from py_crawling_goodies.redis.queues import RedisJsonLIFOQueue


@pytest.fixture(scope='function')
def redis_db():
    """Test that we're using testing redis database,
    load function level fixture, ensure
    database will be flushed after execution of the test function"""
    db_uri = 'redis://localhost:6379/15'
    r = redis.from_url(db_uri)

    assert r.ping() is True
    yield r

    r.flushdb()


def test_redis_lifo_queue(redis_db):
    q = RedisJsonLIFOQueue('pcg:test-queue', r=redis_db)

    # check db property
    assert isinstance(q.db, redis.client.Redis)

    # put / get
    assert q.put({'alice': 1}) == 1
    assert q.get() == {'alice': 1}

    # check if empty
    assert q.is_empty() is True

    # get from empty queue
    assert q.get() is None

    # add few
    assert q.put({'a': 1}) == 1
    assert q.put({'a': 2}) == 2

    # check not empty
    assert q.is_empty() is False

    # put bulk
    items = [{'b': 1}, {'b': 2}, {'b': 3}]
    assert q.put_bulk(items) is True

    # len
    assert len(q) == 5

    # get block
    assert q.get_block() == {'a': 1}

    # get bulk
    assert len(q.get_bulk(2)) == 2
    assert len(q.get_bulk(10)) == 2
