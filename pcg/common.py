import importlib


class ItemSerializer(object):
    __slots__ = {
        '__serializer',
        '__loads',
        '__dumps'
    }

    @property
    def serializer(self) -> str:
        return self.__serializer

    def __init__(self, serializer='json'):
        """Use following serializer for json-like data:

        + json - python standard json
        + ujson - fast implementation
        + rapidjson - fast implementation
        + bson.json_util - to serialize datetime and so on
        + bson - serialize to binary format
        """
        assert serializer in ['json', 'ujson', 'rapidjson',
                              'bson.json_util', 'bson']
        self.__serializer = serializer
        _importer = importlib.import_module

        if self.__serializer == 'bson':
            self.__loads = _importer(self.__serializer).BSON.decode
            self.__dumps = _importer(self.__serializer).BSON.encode
        else:
            self.__loads = _importer(self.__serializer).loads
            self.__dumps = _importer(self.__serializer).dumps

    def loads(self, item):
        return self.__loads(item)

    def dumps(self, item):
        return self.__dumps(item)
