from _version import __version__

API_VERSION = '0.1'

import time

class Client:
    pass

class Record:
    def __init__(self, layer, id, lat, lon, type='object', created=None, **kwargs):
        self.layer = layer
        self.id = id
        self.lon = lon
        self.lat = lat
        self.type = type
        if created is None:
            self.created = int(time.time())
        else:
            self.created = created
        self.__dict__.update(kwargs)

    @classmethod
    def from_dict(cls, data):
        assert data
        coord = data['geometry']['coordinates']
        record = cls(data['properties']['layer'], data['id'], lat=coord[1], lon=coord[0])
        record.type = data['properties']['type']
        record.created = data.get('created', record.created)
        record.__dict__.update(dict((k, v) for k, v in data['properties'].iteritems()
                                    if k not in ('layer', 'type', 'created')))
        return record

class APIError:
    pass
