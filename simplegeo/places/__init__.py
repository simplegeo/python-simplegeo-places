from _version import __version__

API_VERSION = '0.1'

from httplib2 import Http
import oauth2 as oauth
from urlparse import urljoin
import time

from jsonutil import jsonutil as json

class Client(object):
    realm = "http://api.simplegeo.com"
    debug = False
    endpoints = {
        'record': 'record/%(layer)s/%(id)s.json',
        'records': 'records/%(layer)s.json',
    }

    def __init__(self, key, secret, api_version=API_VERSION, host="api.simplegeo.com", port=80):
        self.host = host
        self.port = port
        self.consumer = oauth.Consumer(key, secret)
        self.key = key
        self.secret = secret
        self.api_version = api_version
        self.signature = oauth.SignatureMethod_HMAC_SHA1()
        self.uri = "http://%s:%s" % (host, port)
        self.http = Http()

    def endpoint(self, name, **kwargs):
        try:
            endpoint = self.endpoints[name]
        except KeyError:
            raise Exception('No endpoint named "%s"' % name)
        try:
            endpoint = endpoint % kwargs
        except KeyError, e:
            raise TypeError('Missing required argument "%s"' % (e.args[0],))
        return urljoin(urljoin(self.uri, self.api_version + '/'), endpoint)

    def add_record(self, record):
        if not hasattr(record, 'layer'):
            raise Exception("Record has no layer.")

        endpoint = self.endpoint('record', layer=record.layer, id=record.id)
        self._request(endpoint, "PUT", record.to_json())

    def add_records(self, layer, records):
        features = {
            'type': 'FeatureCollection',
            'features': [record.to_dict() for record in records],
        }
        endpoint = self.endpoint('records', layer=layer)
        self._request(endpoint, "POST", json.dumps(features))

    def _request(self, endpoint, method, data=None):
        body = None
        params = {}
        if method == "GET" and isinstance(data, dict):
            endpoint = endpoint + '?' + urllib.urlencode(data)
        else:
            if isinstance(data, dict):
                body = urllib.urlencode(data)
            else:
                body = data
        if self.debug:
            print endpoint
        request = oauth.Request.from_consumer_and_token(self.consumer,
            http_method=method, http_url=endpoint, parameters=params)

        request.sign_request(self.signature, self.consumer, None)
        headers = request.to_header(self.realm)
        headers['User-Agent'] = 'SimpleGeo Places Client v%s' % __version__

        resp, content = self.http.request(endpoint, method, body=body, headers=headers)

        if self.debug:
            print resp
            print content

        if content: # Empty body is allowed.
            try:
                content = json.loads(content)
            except ValueError:
                raise DecodeError(resp, content)

        if resp['status'][0] != '2':
            code = resp['status']
            message = content
            if isinstance(content, dict):
                code = content['code']
                message = content['message']
            raise APIError(code, message, resp)

        return content

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

    def to_dict(self):
        return {
            'type': 'Feature',
            'id': self.id,
            'created': self.created,
            'geometry': {
                'type': 'Point',
                'coordinates': [self.lon, self.lat],
            },
            'properties': dict((k, v) for k, v in self.__dict__.iteritems() 
                                        if k not in ('lon', 'lat', 'id', 'created')),
        }

    def to_json(self):
        return json.dumps(self.to_dict())


class APIError(Exception):
    """Base exception for all API errors."""

    def __init__(self, code, msg, headers):
        self.code = code
        self.msg = msg
        self.headers = headers

    def __getitem__(self, key):
        if key == 'code':
            return self.code

        try:
            return self.headers[key]
        except KeyError:
            raise AttributeError(key)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "%s (#%s)" % (self.msg, self.code)

