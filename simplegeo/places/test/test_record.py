import unittest
from simplegeo.places import Record
import mock
from decimal import Decimal as D

class RecordTest(unittest.TestCase):

    @mock.patch('time.time')
    def test_record_constructor(self, mock_time):
        mock_time.return_value = 100
        record = Record('my_layer', 'my_id', D('11.0'), D('10.0'))
        self.failUnlessEqual(record.layer, 'my_layer')
        self.failUnlessEqual(record.id, 'my_id')
        self.failUnlessEqual(record.lat, D('11.0'))
        self.failUnlessEqual(record.lon, D('10.0'))
        self.failUnlessEqual(record.created, 100)

        mock_time.return_value = 101
        record = Record('my_layer', 'my_id', D('11.0'), D('10.0'), created=102)
        self.failUnlessEqual(record.layer, 'my_layer')
        self.failUnlessEqual(record.id, 'my_id')
        self.failUnlessEqual(record.lat, D('11.0'))
        self.failUnlessEqual(record.lon, D('10.0'))
        self.failUnlessEqual(record.created, 102)

        mock_time.return_value = 103
        record = Record('my_layer', 'my_id', 11.0, 10.0)
        self.failUnlessEqual(record.layer, 'my_layer')
        self.failUnlessEqual(record.id, 'my_id')
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
                     'id' : 'my_id',
                     'type' : 'Feature',
                     'properties' : {
                                     'layer' : 'my_layer',
                                     'key' : 'value'  ,
                                     'type' : 'object'
                                     }
                     }

        record = Record.from_dict(record_dict)
        self.assertEquals(record.lat, D('11.0'))
        self.assertEquals(record.lon, D('10.0'))
        self.assertEquals(record.id, 'my_id')
        self.assertEquals(record.layer, 'my_layer')
        self.assertEquals(record.key, 'value')
        self.assertEquals(record.type, 'object')
        self.assertEquals(record.created, 99)

        record_dict = { 'created' : 98,
                     'geometry' : {
                                   'type' : 'Point',
                                   'coordinates' : [D('10.03'), D('11.0')]
                                   },
                     'id' : 'my_id',
                     'type' : 'Feature',
                     'properties' : {
                                     'layer' : 'my_layer',
                                     'key' : 'value'  ,
                                     'type' : 'object'
                                     }
                     }

        record = Record.from_dict(record_dict)
        self.assertEquals(record.lat, D('11.0'))
        self.assertEquals(record.lon, D('10.03'))
        self.assertEquals(record.id, 'my_id')
        self.assertEquals(record.layer, 'my_layer')
        self.assertEquals(record.key, 'value')
        self.assertEquals(record.type, 'object')
        self.assertEquals(record.created, 98)

        self.assertEquals('{"geometry": {"type": "Point", "coordinates": [10.03, 11.0]}, "properties": {"layer": "my_layer", "type": "object", "key": "value"}, "type": "Feature", "id": "my_id", "created": 98}', record.to_json())

        record_dict = { 'created' : 97,
                     'geometry' : {
                                   'type' : 'Point',
                                   'coordinates' : [10.0, 11.0]
                                   },
                     'id' : 'my_id',
                     'type' : 'Feature',
                     'properties' : {
                                     'layer' : 'my_layer',
                                     'key' : 'value'  ,
                                     'type' : 'object'
                                     }
                     }

        record = Record.from_dict(record_dict)
        self.assertEquals(record.lat, 11.0)
        self.assertEquals(record.lon, 10.0)
        self.assertEquals(record.id, 'my_id')
        self.assertEquals(record.layer, 'my_layer')
        self.assertEquals(record.key, 'value')
        self.assertEquals(record.type, 'object')
        self.assertEquals(record.created, 97)

        self.assertEquals('{"geometry": {"type": "Point", "coordinates": [10.0, 11.0]}, "properties": {"layer": "my_layer", "type": "object", "key": "value"}, "type": "Feature", "id": "my_id", "created": 97}', record.to_json())
