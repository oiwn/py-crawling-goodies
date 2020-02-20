import redis
import pytest


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
