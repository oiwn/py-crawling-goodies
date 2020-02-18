import importlib


class ItemSerializer(object):
    def __init__(self, serializer='json'):
        assert serializer in ['json', 'ujson', 'rapidjson',
                              'bson.json_util', 'bson']
        self.serializer = serializer
        _importer = importlib.import_module

        if self.serializer == 'bson':
            self.sloads = _importer(self.serializer).BSON.decode
            self.sdumps = _importer(self.serializer).BSON.encode
        else:
            self.sloads = _importer(self.serializer).loads
            self.sdumps = _importer(self.serializer).dumps

    def loads(self, item):
        return self.sloads(item)

    def dumps(self, item):
        return self.sdumps(item)
