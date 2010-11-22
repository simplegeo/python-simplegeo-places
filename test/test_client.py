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

API_VERSION = '0.2'
API_HOST = 'api.simplegeo.com'
API_PORT = 80

class ClientTest(unittest.TestCase):
    def setUp(self):
        self.client = Client(MY_OAUTH_KEY, MY_OAUTH_SECRET, API_VERSION, API_HOST, API_PORT)
        self.created_records = []
        self.record_id = 0
        self.record_lat = D('37.8016')
        self.record_lon = D('-122.4783')

    def _record(self):
        self.record_id += 1
        self.record_lat = (self.record_lat + 10) % 90
        self.record_lon = (self.record_lon + 10) % 180

        return Record(
            layer=TESTING_LAYER,
            id=str(self.record_id),
            lat=self.record_lat,
            lon=self.record_lon
        )

    def test_add_record(self):
        mockhttp = mock.Mock()
        mockhttp.request.return_value = ({'status': '200', 'content-type': 'application/json'}, None)
        self.client.http = mockhttp
        record = self._record()
        self.client.add_record(record)
        self.failUnlessEqual(mockhttp.method_calls[0][0], 'request')
        self.failUnlessEqual(mockhttp.method_calls[0][1][0], 'http://api.simplegeo.com:80/%s/record/TESTING_LAYER/1.json' % (API_VERSION,))
        self.failUnlessEqual(mockhttp.method_calls[0][1][1], 'PUT')
        self.failUnlessEqual(mockhttp.method_calls[0][2]['body'], record.to_json())

    def test_multi_record_post(self):
        feats = [self._record() for i in range(10)]
        featcoll = {
            'type': 'FeatureCollection',
            'features': [feat.to_dict() for feat in feats],
            }

        mockhttp = mock.Mock()
        mockhttp.request.return_value = ({'status': '200', 'content-type': 'application/json'}, None)
        self.client.http = mockhttp

        self.client.add_records(TESTING_LAYER, feats)

        self.failUnlessEqual(mockhttp.method_calls[0][0], 'request')
        self.failUnlessEqual(mockhttp.method_calls[0][1][0], 'http://api.simplegeo.com:80/%s/records/TESTING_LAYER.json' % (API_VERSION,))
        self.failUnlessEqual(mockhttp.method_calls[0][1][1], 'POST')
        self.failUnlessEqual(mockhttp.method_calls[0][2]['body'], json.dumps(featcoll))
