from _version import __version__

API_VERSION = '1.0'

import copy
from httplib2 import Http
import oauth2 as oauth
from urlparse import urljoin
import time
import re

from pyutil import jsonutil as json
from pyutil.assertutil import precondition

def json_decode(jsonstr):
    try:
        return json.loads(jsonstr)
    except (ValueError, TypeError), le:
        raise DecodeError(jsonstr, le)

SIMPLEGEOHANDLE_RSTR=r"""SG_[A-Za-z0-9]{22}(?:_-?[0-9]{1,3}(?:\.[0-9]+)?_-?[0-9]{1,3}(?:\.[0-9]+)?)?(?:@[0-9]+)?$"""
SIMPLEGEOHANDLE_R= re.compile(SIMPLEGEOHANDLE_RSTR)
def is_simplegeohandle(s):
    return isinstance(s, basestring) and SIMPLEGEOHANDLE_R.match(s)

PLACES_URL_R=re.compile("http://(.*)/features/([A-Za-z_,-]*).json$")

def get_simplegeohandle_from_url(u):
    mo = PLACES_URL_R.match(u)
    if not mo:
        raise Exception("This is not a SimpleGeo Places URL: %s" % (u,))
    handle = mo.group(2)
    assert is_simplegeohandle(handle)
    return mo.group(2)

class Client(object):
    realm = "http://api.simplegeo.com"
    endpoints = {
        'endpoints': 'endpoints.json',
        'features': 'features/%(simplegeohandle)s.json',
        'create': 'places',
        'search': 'places/%(lat)s,%(lon)s.json?q=%(query)s&category=%(category)s',
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
        endpoint = self.endpoint('endpoints')
        return json_decode(self._request(endpoint, "GET")[1])

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
        """Create a new record, returns the simplegeohandle. """
        endpoint = self.endpoint('create')
        if record.id:
            # only simplegeohandles or None should be stored in self.id
            assert is_simplegeohandle(record.id)
            raise ValueError('A record cannot be added to the Places database when it already has a simplegeohandle: %s' % (record.id,))
        jsonrec = record.to_json()
        resp, content = self._request(endpoint, "POST", jsonrec)
        if resp['status'] != "202":
            raise APIError(int(resp['status']), content, resp)
        contentobj = json_decode(content)
        if not contentobj.has_key('id'):
            raise APIError(int(resp['status']), content, resp)
        handle = contentobj['id']
        assert is_simplegeohandle(handle)
        return handle

    def get_record(self, simplegeohandle):
        """Return a record for a place."""
        precondition(is_simplegeohandle(simplegeohandle), "simplegeohandle is required to match the regex %s" % SIMPLEGEOHANDLE_RSTR, simplegeohandle=simplegeohandle)
        endpoint = self.endpoint('features', simplegeohandle=simplegeohandle)
        return Record.from_json(self._request(endpoint, 'GET')[1])

    def update_record(self, record):
        """Update a record."""
        endpoint = self.endpoint('features', simplegeohandle=record.id)
        return self._request(endpoint, 'POST', record.to_json())[1]

    def delete_record(self, simplegeohandle):
        """Delete a record."""
        precondition(is_simplegeohandle(simplegeohandle), "simplegeohandle is required to match the regex %s" % SIMPLEGEOHANDLE_RSTR, simplegeohandle=simplegeohandle)
        endpoint = self.endpoint('features', simplegeohandle=simplegeohandle)
        return self._request(endpoint, 'DELETE')[1]

    def search(self, lat, lon, query='', category=''):
        """Search for places near a lat/lon."""
        endpoint = self.endpoint('search', lat=lat, lon=lon, query=query, category=category)
        result = self._request(endpoint, 'GET')[1]

        fc = json_decode(result)
        return [Record.from_dict(f) for f in fc['features']]

    def _request(self, endpoint, method, data=None):
        """
        Not used directly by code external to this lib. Performs the
        actual request against the API, including passing the
        credentials with oauth.  Returns a tuple of (headers as dict,
        body as string).
        """
        if data is not None and not isinstance(data, basestring):
             raise TypeError("data is required to be None or a string or unicode, not %s" % (type(data),))
        params = {}
        body = data
        request = oauth.Request.from_consumer_and_token(self.consumer,
            http_method=method, http_url=endpoint, parameters=params)

        request.sign_request(self.signature, self.consumer, None)
        headers = request.to_header(self.realm)
        headers['User-Agent'] = 'SimpleGeo Places Client v%s' % __version__

        resp, content = self.http.request(endpoint, method, body=body, headers=headers)

        if resp['status'][0] not in ('2', '3'):
            raise APIError(int(resp['status']), content, resp)

        return resp, content

class Record:
    def __init__(self, lat, lon, simplegeohandle=None, type='object', created=None, properties=None):
        """
        The simplegeohandle and the record_id are both optional -- you
        can have one or the other or both or neither.

        A simplegeohandle is globally unique and is assigned by the
        Places service. It is returned from the Places service in the
        response to a request to add a place to the Places database
        (the add_record method).

        The simplegeohandle is passed in as an argument to the
        constructor, named "simplegeohandle", and is stored in the
        "id" attribute of the Record instance.

        A record_id is scoped to your particular user account and is
        chosen by you. The only use for the record_id is in case you
        call add_record and you have already previously added that
        record to the database -- if there is already a record from
        your user account with the same record_id then the Places
        service will return that record to you, along with that
        records simplegeohandle, instead of making a second, duplicate
        record.

        A record_id is passed in as a value in the properties dict
        named "record_id".
        """
        precondition(simplegeohandle is None or is_simplegeohandle(simplegeohandle), "simplegeohandle is required to be None or to match the regex %s" % SIMPLEGEOHANDLE_RSTR, simplegeohandle=simplegeohandle)
        record_id = properties and properties.get('record_id') or None
        precondition(record_id is None or isinstance(record_id, basestring), "record_id is required to be None or a string.", record_id=record_id, properties=properties)
        self.id = simplegeohandle
        self.lon = lon
        self.lat = lat
        self.type = type
        if created is None:
            self.created = int(time.time())
        else:
            self.created = created
        self.properties = {}
        if properties:
            self.properties.update(properties)

    @classmethod
    def from_dict(cls, data):
        assert isinstance(data, dict), (type(data), repr(data))
        coord = data['geometry']['coordinates']
        record = cls(
            simplegeohandle=data.get('id'),
            lat=coord[1],
            lon=coord[0],
            properties=data.get('properties')
            )
        record.created = data.get('created', record.created)
        return record

    def to_dict(self):
        res = {
            'type': 'Feature',
            'id': self.id,
            'created': self.created,
            'geometry': {
                'type': 'Point',
                'coordinates': [self.lon, self.lat],
            },
            'properties': copy.deepcopy(self.properties),
        }
        return res

    @classmethod
    def from_json(cls, jsonstr):
        return cls.from_dict(json_decode(jsonstr))

    def to_json(self):
        return json.dumps(self.to_dict())


class APIError(Exception):
    """Base exception for all API errors."""

    def __init__(self, code, msg, headers, description=''):
        self.code = code
        self.msg = msg
        self.headers = headers
        self.description = description

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "%s (#%s) %s" % (self.msg, self.code, self.description)

class DecodeError(APIError):
    """There was a problem decoding the API's JSON response."""

    def __init__(self, body, le):
        super(DecodeError, self).__init__(None, "Could not decode JSON", None, repr(le))
        self.body = body

    def __repr__(self):
        return "%s content: %s" % (self.description, self.body)
