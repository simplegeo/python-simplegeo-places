import unittest
from simplegeo.places import Record
import mock
from decimal import Decimal as D

class RecordTest(unittest.TestCase):

    @mock.patch('time.time')
    def test_record_constructor(self, mock_time):
        mock_time.return_value = 100
        record = Record(D('11.0'), D('10.0'), properties={'record_id': 'my_id'})
        self.failUnlessEqual(record.properties.get('record_id'), 'my_id')
        self.failUnlessEqual(record.id, None)
        self.failUnlessEqual(record.lat, D('11.0'))
        self.failUnlessEqual(record.lon, D('10.0'))
        self.failUnlessEqual(record.created, 100)

        record = Record(D('11.0'), D('10.0'), simplegeohandle='SG_abcdefghijklmnopqrstuv')
        self.failUnlessEqual(record.properties.get('record_id'), None)
        self.failUnlessEqual(record.id, 'SG_abcdefghijklmnopqrstuv')
        self.failUnlessEqual(record.lat, D('11.0'))
        self.failUnlessEqual(record.lon, D('10.0'))
        self.failUnlessEqual(record.created, 100)

        record = Record(D('11.0'), D('10.0'), properties={'record_id': 'my_id'}, simplegeohandle='SG_abcdefghijklmnopqrstuv')
        self.failUnlessEqual(record.properties.get('record_id'), 'my_id')
        self.failUnlessEqual(record.id, 'SG_abcdefghijklmnopqrstuv')
        self.failUnlessEqual(record.lat, D('11.0'))
        self.failUnlessEqual(record.lon, D('10.0'))
        self.failUnlessEqual(record.created, 100)

        record = Record(D('11.0'), D('10.0'))
        self.failUnlessEqual(record.properties.get('record_id'), None)
        self.failUnlessEqual(record.id, None)
        self.failUnlessEqual(record.lat, D('11.0'))
        self.failUnlessEqual(record.lon, D('10.0'))
        self.failUnlessEqual(record.created, 100)

        mock_time.return_value = 101
        record = Record(D('11.0'), D('10.0'), properties={'record_id': 'my_id'}, created=102)
        self.failUnlessEqual(record.properties.get('record_id'), 'my_id')
        self.failUnlessEqual(record.lat, D('11.0'))
        self.failUnlessEqual(record.lon, D('10.0'))
        self.failUnlessEqual(record.created, 102)

        mock_time.return_value = 103
        record = Record(11.0, 10.0, properties={'record_id': 'my_id'})
        self.failUnlessEqual(record.properties.get('record_id'), 'my_id')
        self.failUnlessEqual(record.lat, 11.0)
        self.failUnlessEqual(record.lon, 10.0)
        self.failUnlessEqual(record.created, 103)

    @mock.patch('time.time')
    def test_record_from_dict(self, mock_time):
        mock_time.return_value = 99
        record_dict = {
                     'geometry' : {
                                   'type' : 'Point',
                                   'coordinates' : [D('10.0'), D('11.0')]
                                   },
                     'type' : 'Feature',
                     'properties' : {
                                     'record_id' : 'my_id',
                                     'key' : 'value'  ,
                                     'type' : 'object'
                                     }
                     }

        record = Record.from_dict(record_dict)
        self.assertEquals(record.lat, D('11.0'))
        self.assertEquals(record.lon, D('10.0'))
        self.assertEquals(record.properties.get('record_id'), 'my_id')
        self.assertEquals(record.properties['key'], 'value')
        self.assertEquals(record.properties['type'], 'object')
        self.assertEquals(record.created, 99)

        record_dict = {
                     'geometry' : {
                                   'type' : 'Point',
                                   'coordinates' : [D('10.0'), D('11.0')]
                                   },
                     'id' : 'SG_abcdefghijklmnopqrstuv',
                     'type' : 'Feature',
                     'properties' : {
                                     'key' : 'value'  ,
                                     'type' : 'object'
                                     }
                     }

        record = Record.from_dict(record_dict)
        self.assertEquals(record.lat, D('11.0'))
        self.assertEquals(record.lon, D('10.0'))
        self.assertEquals(record.properties.get('record_id'), None)
        self.assertEquals(record.id, 'SG_abcdefghijklmnopqrstuv')
        self.assertEquals(record.properties.get('key'), 'value')
        self.assertEquals(record.properties.get('type'), 'object')
        self.assertEquals(record.created, 99)

        record_dict = {
                     'geometry' : {
                                   'type' : 'Point',
                                   'coordinates' : [D('10.0'), D('11.0')]
                                   },
                     'id' : 'SG_abcdefghijklmnopqrstuv',
                     'type' : 'Feature',
                     'properties' : {
                                     'record_id' : 'my_id',
                                     'key' : 'value'  ,
                                     'type' : 'object'
                                     }
                     }

        record = Record.from_dict(record_dict)
        self.assertEquals(record.lat, D('11.0'))
        self.assertEquals(record.lon, D('10.0'))
        self.assertEquals(record.properties.get('record_id'), 'my_id')
        self.assertEquals(record.id, 'SG_abcdefghijklmnopqrstuv')
        self.assertEquals(record.properties.get('key'), 'value')
        self.assertEquals(record.properties.get('type'), 'object')
        self.assertEquals(record.created, 99)

        record_dict = {
                     'geometry' : {
                                   'type' : 'Point',
                                   'coordinates' : [D('10.0'), D('11.0')]
                                   },
                     'type' : 'Feature',
                     'properties' : {
                                     'key' : 'value'  ,
                                     'type' : 'object'
                                     }
                     }

        record = Record.from_dict(record_dict)
        self.assertEquals(record.lat, D('11.0'))
        self.assertEquals(record.lon, D('10.0'))
        self.assertEquals(record.properties.get('record_id'), None)
        self.assertEquals(record.id, None)
        self.assertEquals(record.properties.get('key'), 'value')
        self.assertEquals(record.properties.get('type'), 'object')
        self.assertEquals(record.created, 99)

        record_dict = { 'created' : 98,
                     'geometry' : {
                                   'type' : 'Point',
                                   'coordinates' : [D('10.03'), D('11.0')]
                                   },
                     'type' : 'Feature',
                     'properties' : {
                                     'record_id' : 'my_id',
                                     'key' : 'value'  ,
                                     'type' : 'object'
                                     }
                     }

        record = Record.from_dict(record_dict)
        self.assertEquals(record.lat, D('11.0'))
        self.assertEquals(record.lon, D('10.03'))
        self.assertEquals(record.properties.get('record_id'), 'my_id')
        self.assertEquals(record.properties.get('key'), 'value')
        self.assertEquals(record.properties.get('type'), 'object')
        self.assertEquals(record.created, 98)

        record_dict = { 'created' : 97,
                     'geometry' : {
                                   'type' : 'Point',
                                   'coordinates' : [10.0, 11.0]
                                   },
                     'type' : 'Feature',
                     'properties' : {
                                     'record_id' : 'my_id',
                                     'key' : 'value'  ,
                                     'type' : 'object'
                                     }
                     }

        record = Record.from_dict(record_dict)
        self.assertEquals(record.lat, 11.0)
        self.assertEquals(record.lon, 10.0)
        self.assertEquals(record.properties.get('record_id'), 'my_id')
        self.assertEquals(record.properties.get('key'), 'value')
        self.assertEquals(record.properties.get('type'), 'object')
        self.assertEquals(record.created, 97)

    def test_record_to_dict_sets_id_correctly(self):
        handle = 'SG_abcdefghijklmnopqrstuv'
        record_id = 'this is my record #1. my first record. and it is mine'
        rec = Record(D('11.03'), D('10.03'), simplegeohandle=handle, properties={'record_id': record_id})
        dic = rec.to_dict()
        self.failUnlessEqual(dic.get('id'), handle)
        self.failUnlessEqual(dic.get('properties', {}).get('record_id'), record_id)

        rec = Record(D('11.03'), D('10.03'), simplegeohandle=handle, properties={'record_id': None})
        dic = rec.to_dict()
        self.failUnlessEqual(dic.get('id'), handle)
        self.failUnlessEqual(dic.get('properties', {}).get('record_id'), None)

        rec = Record(D('11.03'), D('10.03'), simplegeohandle=handle, properties={'record_id': None})
        dic = rec.to_dict()
        self.failUnlessEqual(dic.get('id'), handle)
        self.failUnlessEqual(dic.get('properties', {}).get('record_id'), None)

        rec = Record(D('11.03'), D('10.03'), simplegeohandle=None, properties={'record_id': None})
        dic = rec.to_dict()
        self.failUnlessEqual(dic.get('id'), None)
        self.failUnlessEqual(dic.get('properties', {}).get('record_id'), None)
