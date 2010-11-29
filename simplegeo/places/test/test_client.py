import time
import random
import unittest
from jsonutil import jsonutil as json
import random
from simplegeo.places import Client, Record, APIError

from decimal import Decimal as D

import os

import mock

MY_OAUTH_KEY = 'MY_OAUTH_KEY'
MY_OAUTH_SECRET = 'MY_SECRET_KEY'
TESTING_LAYER = 'TESTING_LAYER'

API_VERSION = '1.0'
API_HOST = 'api.simplegeo.com'
API_PORT = 80

ENDPOINT_DESCR=json.dumps({
        "GET /1.0/places/<place_id:[a-zA-Z0-9\\.,_-]+>.json": "Return a record for a place.",
        "GET /1.0/endpoints.json": "Describe known endpoints.",
        "POST /1.0/places/<place_id:.*>.json": "Update a record.",
        "GET /1.0/places/<lat:-?[0-9\\.]+>,<lon:-?[0-9\\.]+>/search.json": "Search for places near a lat/lon. Query string includes ?q=term and ?q=term&category=cat",
        "PUT /1.0/places/place.json": "Create a new record, returns a 301 to the location of the resource.",
        "GET /1.0/debug/<number:\\d+>": "Undocumented.",
        "DELETE /1.0/places/<place_id:.*>.json": "Delete a record."})

class ClientTest(unittest.TestCase):
    def setUp(self):
        self.client = Client(MY_OAUTH_KEY, MY_OAUTH_SECRET, API_VERSION, API_HOST, API_PORT)

    def test_wrong_endpoint(self):
        self.assertRaises(Exception, self.client.endpoint, 'recordt')

    def test_missing_argument(self):
        self.assertRaises(Exception, self.client.endpoint, 'record')

    def test_endpoint_descriptions(self):
        mockhttp = mock.Mock()
        mockhttp.request.return_value = ({'status': '200', 'content-type': 'application/json'}, ENDPOINT_DESCR)
        self.client.http = mockhttp
        d = self.client.get_endpoint_descriptions()
        self.failUnless(isinstance(d, dict), d)

    def test_add_record(self):
        mockhttp = mock.Mock()
        newloc = 'http://api.simplegeo.com:80/%s/places/abcdefghijklmnopqrstuvwyz.json' % (API_VERSION,)
        mockhttp.request.return_value = ({'status': '301', 'content-type': 'application/json', 'location': newloc}, json.dumps("Yo dawg, go to the new location: '%s'" % (newloc,)))
        self.client.http = mockhttp

        record = Record(
            layer=TESTING_LAYER,
            id=str(1),
            lat=D('37.8016'),
            lon=D('-122.4783')
        )

        self.client.add_record(record)
        self.assertEqual(mockhttp.method_calls[0][0], 'request')
        self.assertEqual(mockhttp.method_calls[0][1][0], 'http://api.simplegeo.com:80/%s/places/place.json' % (API_VERSION,))
        self.assertEqual(mockhttp.method_calls[0][1][1], 'PUT')
        self.assertEqual(mockhttp.method_calls[0][2]['body'], record.to_json())

    def test_get_record(self):
        simplegeoid = 'abcdefghijklmnopqrstuvwyz'
        resultrecord = Record('a_layer', simplegeoid, D('11.03'), D('10.03'))

        mockhttp = mock.Mock()
        mockhttp.request.return_value = ({'status': '200', 'content-type': 'application/json', }, resultrecord.to_json())
        self.client.http = mockhttp

        res = self.client.get_record(simplegeoid)
        self.assertEqual(mockhttp.method_calls[0][0], 'request')
        self.assertEqual(mockhttp.method_calls[0][1][0], 'http://api.simplegeo.com:80/%s/places/%s.json' % (API_VERSION, simplegeoid))
        self.assertEqual(mockhttp.method_calls[0][1][1], 'GET')
        self.failUnless(isinstance(res, Record), res)
        self.assertEqual(res.to_json(), resultrecord.to_json())

    def test_update_record(self):
        simplegeoid = 'abcdefghijklmnopqrstuvwyz'
        rec = Record('a_layer', simplegeoid, D('11.03'), D('10.04'))

        mockhttp = mock.Mock()
        mockhttp.request.return_value = ({'status': '200', 'content-type': 'application/json', }, rec.to_json())
        self.client.http = mockhttp

        res = self.client.update_record(rec)
        self.failUnlessEqual(res.to_json(), rec.to_json())

    def test_delete_record(self):
        simplegeoid = 'abcdefghijklmnopqrstuvwyz'
        rec = Record('a_layer', simplegeoid, D('11.03'), D('10.04'))

        mockhttp = mock.Mock()
        mockhttp.request.return_value = ({'status': '200', 'content-type': 'application/json', }, rec.to_json())
        self.client.http = mockhttp

        res = self.client.delete_record(simplegeoid)
        self.failUnlessEqual(res.to_json(), rec.to_json())

    def test_search(self):
        rec1 = Record('abcdefghijkmlnopqrstuvwyz1', D('11.03'), D('10.04'), type='place', name="Bob's House Of Monkeys", category="monkey dealership")
        rec2 = Record('abcdefghijkmlnopqrstuvwyz2', D('11.03'), D('10.05'), type='place', name="Monkey Food 'R' Us", category="pet food store")

        mockhttp = mock.Mock()
        mockhttp.request.return_value = ({'status': '200', 'content-type': 'application/json', }, json.dumps([rec1.to_dict(), rec2.to_dict()]))
        self.client.http = mockhttp

        res = self.client.search(D('11.03'), D('10.04'), query='monkeys', category='animal')
        self.failUnlessEqual(len(res), 2)
        self.failUnlessEqual(res[0], rec1.to_dict())
