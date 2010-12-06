import unittest
from simplegeo.places import Record
import mock
from decimal import Decimal as D

class RecordTest(unittest.TestCase):

    @mock.patch('time.time')
    def test_record_constructor(self, mock_time):
        mock_time.return_value = 100
        record = Record(D('11.0'), D('10.0'), recordid='my_id')
        self.failUnlessEqual(record.recordid, 'my_id')
        self.failUnlessEqual(record.simplegeohandle, None)
        self.failUnlessEqual(record.lat, D('11.0'))
        self.failUnlessEqual(record.lon, D('10.0'))
        self.failUnlessEqual(record.created, 100)

        record = Record(D('11.0'), D('10.0'), simplegeohandle='SG_abcdefghijklmnopqrstuvwyz')
        self.failUnlessEqual(record.recordid, None)
        self.failUnlessEqual(record.simplegeohandle, 'SG_abcdefghijklmnopqrstuvwyz')
        self.failUnlessEqual(record.lat, D('11.0'))
        self.failUnlessEqual(record.lon, D('10.0'))
        self.failUnlessEqual(record.created, 100)

        record = Record(D('11.0'), D('10.0'), recordid='my_id', simplegeohandle='SG_abcdefghijklmnopqrstuvwyz')
        self.failUnlessEqual(record.recordid, 'my_id')
        self.failUnlessEqual(record.simplegeohandle, 'SG_abcdefghijklmnopqrstuvwyz')
        self.failUnlessEqual(record.lat, D('11.0'))
        self.failUnlessEqual(record.lon, D('10.0'))
        self.failUnlessEqual(record.created, 100)

        record = Record(D('11.0'), D('10.0'))
        self.failUnlessEqual(record.recordid, None)
        self.failUnlessEqual(record.simplegeohandle, None)
        self.failUnlessEqual(record.lat, D('11.0'))
        self.failUnlessEqual(record.lon, D('10.0'))
        self.failUnlessEqual(record.created, 100)

        mock_time.return_value = 101
        record = Record(D('11.0'), D('10.0'), recordid='my_id', created=102)
        self.failUnlessEqual(record.recordid, 'my_id')
        self.failUnlessEqual(record.lat, D('11.0'))
        self.failUnlessEqual(record.lon, D('10.0'))
        self.failUnlessEqual(record.created, 102)

        mock_time.return_value = 103
        record = Record(11.0, 10.0, recordid='my_id')
        self.failUnlessEqual(record.recordid, 'my_id')
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
                     'recordid' : 'my_id',
                     'type' : 'Feature',
                     'properties' : {
                                     'key' : 'value'  ,
                                     'type' : 'object'
                                     }
                     }

        record = Record.from_dict(record_dict)
        self.assertEquals(record.lat, D('11.0'))
        self.assertEquals(record.lon, D('10.0'))
        self.assertEquals(record.recordid, 'my_id')
        self.assertEquals(record.key, 'value')
        self.assertEquals(record.type, 'object')
        self.assertEquals(record.created, 99)

        record_dict = {
                     'geometry' : {
                                   'type' : 'Point',
                                   'coordinates' : [D('10.0'), D('11.0')]
                                   },
                     'simplegeohandle' : 'SG_abcdefghijklmnopqrstuvwyz',
                     'type' : 'Feature',
                     'properties' : {
                                     'key' : 'value'  ,
                                     'type' : 'object'
                                     }
                     }

        record = Record.from_dict(record_dict)
        self.assertEquals(record.lat, D('11.0'))
        self.assertEquals(record.lon, D('10.0'))
        self.assertEquals(record.recordid, None)
        self.assertEquals(record.simplegeohandle, 'SG_abcdefghijklmnopqrstuvwyz')
        self.assertEquals(record.key, 'value')
        self.assertEquals(record.type, 'object')
        self.assertEquals(record.created, 99)

        record_dict = {
                     'geometry' : {
                                   'type' : 'Point',
                                   'coordinates' : [D('10.0'), D('11.0')]
                                   },
                     'recordid' : 'my_id',
                     'simplegeohandle' : 'SG_abcdefghijklmnopqrstuvwyz',
                     'type' : 'Feature',
                     'properties' : {
                                     'key' : 'value'  ,
                                     'type' : 'object'
                                     }
                     }

        record = Record.from_dict(record_dict)
        self.assertEquals(record.lat, D('11.0'))
        self.assertEquals(record.lon, D('10.0'))
        self.assertEquals(record.recordid, 'my_id')
        self.assertEquals(record.simplegeohandle, 'SG_abcdefghijklmnopqrstuvwyz')
        self.assertEquals(record.key, 'value')
        self.assertEquals(record.type, 'object')
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
        self.assertEquals(record.recordid, None)
        self.assertEquals(record.simplegeohandle, None)
        self.assertEquals(record.key, 'value')
        self.assertEquals(record.type, 'object')
        self.assertEquals(record.created, 99)

        record_dict = { 'created' : 98,
                     'geometry' : {
                                   'type' : 'Point',
                                   'coordinates' : [D('10.03'), D('11.0')]
                                   },
                     'recordid' : 'my_id',
                     'type' : 'Feature',
                     'properties' : {
                                     'key' : 'value'  ,
                                     'type' : 'object'
                                     }
                     }

        record = Record.from_dict(record_dict)
        self.assertEquals(record.lat, D('11.0'))
        self.assertEquals(record.lon, D('10.03'))
        self.assertEquals(record.recordid, 'my_id')
        self.assertEquals(record.key, 'value')
        self.assertEquals(record.type, 'object')
        self.assertEquals(record.created, 98)

        record_dict = { 'created' : 97,
                     'geometry' : {
                                   'type' : 'Point',
                                   'coordinates' : [10.0, 11.0]
                                   },
                     'recordid' : 'my_id',
                     'type' : 'Feature',
                     'properties' : {
                                     'key' : 'value'  ,
                                     'type' : 'object'
                                     }
                     }

        record = Record.from_dict(record_dict)
        self.assertEquals(record.lat, 11.0)
        self.assertEquals(record.lon, 10.0)
        self.assertEquals(record.recordid, 'my_id')
        self.assertEquals(record.key, 'value')
        self.assertEquals(record.type, 'object')
        self.assertEquals(record.created, 97)

    def test_record_to_dict_sets_id_correctly(self):
        handle = 'SG_abcdefghijklmnopqrstuvwyz'
        recordid = 'this is my record #1. my first record. and it is mine'
        rec = Record(D('11.03'), D('10.03'), simplegeohandle=handle, recordid=recordid)
        self.failUnlessRaises(ValueError, rec.to_dict, for_add_record=True)

        rec = Record(D('11.03'), D('10.03'), simplegeohandle=handle, recordid=None)
        self.failUnlessRaises(ValueError, rec.to_dict, for_add_record=True)

        rec = Record(D('11.03'), D('10.03'), simplegeohandle=handle, recordid=None)
        dic = rec.to_dict(for_add_record=False)
        self.failUnlessEqual(dic.get('id'), handle)

        rec = Record(D('11.03'), D('10.03'), simplegeohandle=None, recordid=None)
        dic = rec.to_dict(for_add_record=False)
        self.failUnlessEqual(dic.get('id'), None)
