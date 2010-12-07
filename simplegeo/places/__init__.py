API_VERSION = '1.0'

from pyutil.assertutil import precondition

from simplegeo.shared import APIError, Record, SIMPLEGEOHANDLE_RSTR, is_simplegeohandle, json_decode
from simplegeo.shared import Client as SGClient

endpoints = {
    'endpoints': 'endpoints.json',
    'features': 'features/%(simplegeohandle)s.json',
    'create': 'places',
    'search': 'places/%(lat)s,%(lon)s.json?q=%(query)s&category=%(category)s',
    }

class Client(SGClient):
    def __init__(self, key, secret, api_version=API_VERSION, host="api.simplegeo.com", port=80):
        SGClient.__init__(self, key, secret, api_version=api_version, host=host, port=port)
        self.endpoints.update(endpoints)

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
