from _version import __version__

API_VERSION = '1.0'

from httplib2 import Http
import oauth2 as oauth
from urlparse import urljoin
import time

from jsonutil import jsonutil as json

# {"GET /1.0/places/<place_id:[a-zA-Z0-9\\.,_-]+>.json": "Return a record for a place.", "GET /1.0/endpoints.json": "Describe known endpoints.", "POST /1.0/places/<place_id:.*>.json": "Update a record.", "GET /1.0/places/<lat:-?[0-9\\.]+>,<lon:-?[0-9\\.]+>/search.json": "Search for places near a lat/lon.", "PUT /1.0/places/place.json": "Create a new record, returns a 301 to the location of the resource.", "GET /1.0/debug/<number:\\d+>": "Undocumented.", "DELETE /1.0/places/<place_id:.*>.json": "Delete a record."}


class Client(object):
    realm = "http://api.simplegeo.com"
    endpoints = {
        'endpoints': 'endpoints.json',
        'places': 'places/%(simplegeoid)s.json',
        'place': 'places/place.json',
        'search': 'places/%(lat)s,%(lon)s/search.json?query=%(query)s&category=%(category)s',
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

    def get_endpoint_descriptions(self):
        """Describe known endpoints."""
        return self._request(self.endpoint('endpoints'), 'GET')

    def endpoint(self, name, **kwargs):
        """Not used directly. Finds and formats the endpoints as needed for any type of request."""
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
        """Create a new record, returns a 301 to the location of the resource."""
        endpoint = self.endpoint('place')
        self._request(endpoint, "PUT", record.to_json())

    def get_record(self, simplegeoid):
        """Return a record for a place."""
        endpoint = self.endpoint('places', simplegeoid=simplegeoid)
        return self._request(endpoint, 'GET')

    def update_record(self, record):
        """Update a record."""
        endpoint = self.endpoint('places', simplegeoid=record.id)
        return self._request(endpoint, 'POST')

    def delete_record(self, simplegeoid):
        """Delete a record."""
        endpoint = self.endpoint('places', simplegeoid=simplegeoid)
        return self._request(endpoint, 'DELETE')

    def search(self, lat, lon, query='', category=''):
        """Search for places near a lat/lon."""
        endpoint = self.endpoint('search', lat=lat, lon=lon, query=query, category=category)
        return self._request(endpoint, 'GET')

    def _request(self, endpoint, method, data=None):
        """Not used directly. Performs the actual request against the API, including passing the credentials with oauth. 
        Returns a dict or record object as appropriate."""
        body = None
        params = {}
        if method == "GET" and isinstance(data, dict):
            endpoint = endpoint + '?' + urllib.urlencode(data)
        else:
            if isinstance(data, dict):
                body = urllib.urlencode(data)
            else:
                body = data
        request = oauth.Request.from_consumer_and_token(self.consumer,
            http_method=method, http_url=endpoint, parameters=params)

        request.sign_request(self.signature, self.consumer, None)
        headers = request.to_header(self.realm)
        headers['User-Agent'] = 'SimpleGeo Places Client v%s' % __version__

        resp, content = self.http.request(endpoint, method, body=body, headers=headers)

        if content: # Empty body is allowed.
            try:
                content = json.loads(content)
            except (ValueError, TypeError), le:
                raise DecodeError(resp, content, le)

        if resp['status'][0] not in ('2', '3'):
            code = resp['status']
            message = content
            if isinstance(content, dict):
                code = content['code']
                message = content['message']
            raise APIError(code, message, resp)

        # If this is a record object, return the Python object instead of the dict.
        try:
            content = Record.from_dict(content)
        except (TypeError, KeyError):
            # Okay nevermind I guess it wasn't a Record.
            pass

        return content

class Record:
    def __init__(self, id, lat, lon, type='object', created=None, **kwargs):
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
        record = cls(data['id'], lat=coord[1], lon=coord[0])
        record.type = data['properties']['type']
        record.created = data.get('created', record.created)
        record.__dict__.update(dict((k, v) for k, v in data['properties'].iteritems()
                                    if k not in ('type', 'created')))
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

    def __init__(self, code, msg, headers, description=''):
        self.code = code
        self.msg = msg
        self.headers = headers
        self.description = description

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
        return "%s (#%s) %s" % (self.msg, self.code, self.description)

class DecodeError(APIError):
    """There was a problem decoding the API's JSON response."""

    def __init__(self, headers, body, le):
        super(DecodeError, self).__init__(None, "Could not decode JSON", headers, repr(le))
        self.body = body

    def __repr__(self):
        return "headers: %s, content: <%s> %s" % (self.headers, self.body, self.description)

