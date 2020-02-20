import redis
import pytest
from pcg.redis.filters import RedisSetFilter, RedisBucketFilter


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


def test_redis_set_filter(redis_db):
    f = RedisSetFilter('pcg:test-set', r=redis_db)

    # check db property
    assert isinstance(f.db, redis.client.Redis)

    # add single value
    assert f.add('alice') == 1
    assert len(f.to_set()) == len(f) == 1
    assert isinstance(f.to_set(), set)
    assert f.to_set() == set(['alice'])

    # add few values
    assert f.add('bob', 'jane') == 2
    assert f.add('bob', 'jane') == 0
    assert len(f) == 3

    # remove value
    assert f.remove('jane') is True
    assert f.remove('john') is False
    assert len(f) == 2

    # check existance
    assert f.exists('alice') is True
    assert f.exists('jane') is False

    # data structure in memory size
    f.add('many', 'other', 'people', 'walking', 'around')
    assert len(f) == 7
    assert f.sizeof() > 400

    # check str
    assert 'RedisSetFilter' in str(f)
    assert 'pcg:test-set' in str(f)


def test_redis_bucket_filter(redis_db):
    f = RedisBucketFilter('pcg:test-bucket', r=redis_db, bucket_digits=1)

    # check db property
    assert isinstance(f.db, redis.client.Redis)

    # add single value
    assert f.add('alice') == 1
    assert f.exists('alice') is True
    assert f.exists('bob') is False

    # add few values
    assert f.add('bob', 'john', 'jane') == 3
    assert f.add('bob', 'john', 'jane') == 0
    assert len(f) == 4

    # remove value
    assert f.remove('jane') is True
    assert f.remove('tom') is False

    # check existance
    assert f.exists('alice') is True
    assert f.exists('jane') is False

    # data structure in memory size
    f.add('dome', 'roland', 'krot', 'bes', 'paperclip')
    assert len(f) == 8
    assert f.sizeof() > 800

    # check info about buckets
    assert len(f.info()) == 5
    assert f.info()['pcg:test-bucket:1'] == 3
    assert f.info()['pcg:test-bucket:4'] == 2

    # check str
    assert 'RedisBucketFilter' in str(f)
    assert 'pcg:test-bucket' in str(f)
