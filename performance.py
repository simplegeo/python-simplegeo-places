#!/usr/bin/env python

import random
import time
import numpy

from simplegeo.places import Client
from simplegeo.places import Record, APIError

MY_OAUTH_KEY = ''
MY_OAUTH_SECRET = ''

API_VERSION = '1.0'
API_HOST = ''
#API_HOST = 'api.simplegeo.com'
API_PORT = 80

class PerformanceTest(object):
    def __init__(self, number_of_requests=1):
        self.number_of_requests = number_of_requests
        self.client = Client(MY_OAUTH_KEY, MY_OAUTH_SECRET, API_VERSION, API_HOST, API_PORT)
        self.responses = []
        self.request_test = { 'add_record': self._timed_response_add_record,
                         'get_record': self._timed_response_get_record,
                         'update_record': self._timed_response_get_record,
                         'delete_record': self._timed_response_add_record,
                         'search': self._timed_response_search}
        self.simplegeoids =[]

    def run(self):
        self.performance_test('add_record')
        time.sleep(30)
        self.performance_test('get_record')
        self.performance_test('update_record')        
        self.performance_test('search')

    def performance_test(self, request_type):
        requests_completed = 0 
        requests_failed = 0 

        for i in range(self.number_of_requests):
            try:
                print '\n\nTrying %s request %s\n\n' % (request_type,i) 
                timed_response = self._timed_response(request_type)
                requests_completed += 1
                self.responses.append(timed_response)
            except APIError,ex:
                print ex
                requests_failed += 1
     
        print '\n\n', self.responses
        print '\n\n%s requests completed, %s requests failed' % (requests_completed, requests_failed)

        times = [response['time_elapsed'] for response in self.responses]
        print '\n\nmin: %s max: %s avg: %s\n\n' % (min(times), max(times), (sum(times) / len(times)))
        bins = [i * 0.1 for i in range(20)] + [2.0] + [10.0]
        histogram = numpy.histogram(times, bins=bins)
        frequencies = [frequency for frequency in histogram[0]]
        bins = [bin for bin in histogram[1]]
        for (i, bin) in enumerate(bins):
            print '%ss' % bin 
            try:
                print '\t' + str(frequencies[i]) + '\t' + '=' * frequencies[i]
            except:
                pass

    def _timed_response(self, request_type):
        return self.request_test[request_type]()

    def _timed_response_add_record(self):
        record = self._random_record()
        print 'Timing client.add_record(%s)\n\n' % (record.to_dict())
        start_time = time.time()
        response = self.client.add_record(record)
        time_elapsed = time.time() - start_time
        print 'Time elapsed: %s' % time_elapsed
        self.simplegeoids.append(response);
        return {'record': record.to_dict(),
                'response': response,
                'time_elapsed': time_elapsed}

    def _timed_response_get_record(self):
        sgid = self._random_simplegeoid()
        print 'Timing client.get_record(%s)\n\n' % sgid
        start_time = time.time()
        response = self.client.get_record(sgid)
        time_elapsed = time.time() - start_time
        print 'Time elapsed: %s' % time_elapsed
        return {'sgid': sgid,
                'response': response,
                'time_elapsed': time_elapsed}

    def _timed_response_update_record(self):
        sgid = self._random_simplegeoid()
        record = self.client.get_record(sgid)
        print 'Timing client.update_record(%s,%s)\n\n' % (sgid, record.to_dict())
        #changing the lat/lon to make it a *real* update
        (record.lat,record.lon) = self._random_US_lat_lon()
        start_time = time.time()
        response = self.client.update_record(sgid,record)
        time_elapsed = time.time() - start_time
        print 'Time elapsed: %s' % time_elapsed
        return {'sgid': sgid,
                'record': record.to_dict(),
                'response': response,
                'time_elapsed': time_elapsed}

    def _timed_response_delete_record(self):
        sgid = self._random_simplegeoid()
        simplegeoids.remove(sgid)
        print 'Timing client.delete_record(%s)\n\n' % sgid
        start_time = time.time()
        response = self.client.delete_record(sgid)
        time_elapsed = time.time() - start_time
        print 'Time elapsed: %s' % time_elapsed
        return {'sgid': sgid,
                'response': response,
                'time_elapsed': time_elapsed}

    def _timed_response_search(self):
        (lat,lon) = self._random_US_lat_lon()
        print 'Timing client.search(%s,%s,%s)\n\n' % (lat,lon,'restaurant')
        start_time = time.time()
        response = self.client.search(lat,lon,query='',category='restaurant')
        time_elapsed = time.time() - start_time
        print 'Time elapsed: %s' % time_elapsed
        return {'sgid': sgid,
                'response': response,
                'time_elapsed': time_elapsed}

    def _random_record(self):
        (lat,lon) = self._random_US_lat_lon()
        properties_d = {"name": 'name_%s_%s' % (lat,lon)}
        record = Record(lat, lon, properties=properties_d)
        return record
    def _random_US_lat_lon(self):
        return (random.uniform(25.0, 50.0), random.uniform(-125.0, -65.0))

    def _random_simplegeoid(self):
        if len(self.simplegeoids) < 1:
            print >>sys.stderr, "No more SimplegeoIds to process"
            return ''
        return random.choice(self.simplegeoids)

def main():
    performance_test = PerformanceTest()
    performance_test.run()

if __name__ == '__main__':
    main()

