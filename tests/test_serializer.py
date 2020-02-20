import json
import bson
import pytest
from pcg.common import ItemSerializer


def test_item_serializer():
    # raise serializer lib if not supported
    with pytest.raises(AssertionError):
        ItemSerializer(serializer='musson')

    s = ItemSerializer()  # use standard json serializer

    # check serializer
    assert s.serializer == 'json'

    # check functons type
    assert s._loads == json.loads
    assert s._dumps == json.dumps

    # check functions
    assert s.loads('{"a": 1}') == {'a': 1}
    assert s.dumps({'a': 1}) == '{"a": 1}'

    del s

    # special cases
    s = ItemSerializer(serializer='bson')

    # check serializer
    assert s.serializer == 'bson'

    # check functions type
    assert s._loads == bson.BSON.decode
    assert s._dumps == bson.BSON.encode
