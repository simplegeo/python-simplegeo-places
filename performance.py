#!/usr/bin/env python

import random
import time
import numpy

from simplegeo.places import Client
from simplegeo.shared import Feature, APIError

MY_OAUTH_KEY = ''
MY_OAUTH_SECRET = ''

API_VERSION = '1.0'
API_HOST = ''
#API_HOST = 'api.simplegeo.com'
API_PORT = 80

class PerformanceTest(object):
    def __init__(self, number_of_requests=100):
        self.number_of_requests = number_of_requests
        self.client = Client(MY_OAUTH_KEY, MY_OAUTH_SECRET, API_VERSION, API_HOST, API_PORT)
        self.responses = []
        self.request_test = { 'add_feature': self._timed_response_add_feature,
                         'get_feature': self._timed_response_get_feature,
                         'update_feature': self._timed_response_get_feature,
                         'delete_feature': self._timed_response_add_feature,
                         'search': self._timed_response_search}
        self.simplegeoids =[]

    def run(self):
        self.performance_test('add_feature')
        time.sleep(30)
        self.responses = []
        self.performance_test('get_feature')
        self.responses = []
        self.performance_test('update_feature')
        self.responses = []        
        self.performance_test('search')
        self.responses = []

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

    def _timed_response_add_feature(self):
        feature = self._random_feature()
        print 'Timing: client.add_feature(%s)\n\n' % (feature.to_dict())
        start_time = time.time()
        response = self.client.add_feature(feature)
        time_elapsed = time.time() - start_time
        print 'Headers: %s\n\n' % self.client.get_most_recent_http_headers()
        header_time_elapsed = float(self.client.get_most_recent_http_headers().get('x-response-time', '0').rstrip('ms'))
        print 'Header Time elapsed: %s' % header_time_elapsed
        print 'Time elapsed: %s' % time_elapsed
        self.simplegeoids.append(response);
        return {'feature': feature.to_dict(),
                'response': response,
                'time_elapsed': time_elapsed,
                'header_time_elapsed': header_time_elapsed}

    def _timed_response_get_feature(self):
        sgid = self._random_simplegeoid()
        print 'Timing: client.get_feature(%s)\n\n' % sgid
        start_time = time.time()
        response = self.client.get_feature(sgid)
        time_elapsed = time.time() - start_time
        #print 'Headers: %s\n\n' % self.client.get_most_recent_http_headers()
        header_time_elapsed = float(self.client.get_most_recent_http_headers().get('x-response-time', '0').rstrip('ms'))
        print 'Header Time elapsed: %s' % header_time_elapsed
        print 'Time elapsed: %s' % time_elapsed
        return {'sgid': sgid,
                'response': response,
                'time_elapsed': time_elapsed,
                'header_time_elapsed': header_time_elapsed}

    def _timed_response_update_feature(self):
        sgid = self._random_simplegeoid()
        feature = self.client.get_feature(sgid)
        print 'Timing: client.update_feature(%s,%s)\n\n' % (sgid, feature.to_dict())
        #changing the lat/lon to make it a *real* update
        (feature.lat,feature.lon) = self._random_US_lat_lon()
        start_time = time.time()
        response = self.client.update_feature(sgid,feature)
        time_elapsed = time.time() - start_time
        #print 'Headers: %s\n\n' % self.client.get_most_recent_http_headers()
        header_time_elapsed = self.client.get_most_recent_http_headers()
        print 'Header Time elapsed: %s' % header_time_elapsed
        print 'Time elapsed: %s' % time_elapsed
        return {'sgid': sgid,
                'feature': feature.to_dict(),
                'response': response,
                'time_elapsed': time_elapsed,
                'header_time_elapsed': header_time_elapsed}

    def _timed_response_delete_feature(self):
        sgid = self._random_simplegeoid()
        simplegeoids.remove(sgid)
        print 'Timing: client.delete_feature(%s)\n\n' % sgid
        start_time = time.time()
        response = self.client.delete_feature(sgid)
        time_elapsed = time.time() - start_time
        #print 'Headers: %s\n\n' % self.client.get_most_recent_http_headers()
        header_time_elapsed = self.client.get_most_recent_http_headers()
        print 'Header Time elapsed: %s' % header_time_elapsed
        print 'Time elapsed: %s' % time_elapsed
        return {'sgid': sgid,
                'response': response,
                'time_elapsed': time_elapsed,
                'header_time_elapsed': header_time_elapsed}

    def _timed_response_search(self):
        (lat,lon) = self._random_US_lat_lon()
        print 'Timing: client.search(%s,%s,%s)\n\n' % (lat,lon,'restaurant')
        start_time = time.time()
        response = self.client.search(lat,lon,query='',category='restaurant')
        time_elapsed = time.time() - start_time
        #print 'Headers: %s\n\n' % self.client.get_most_recent_http_headers()
        header_time_elapsed = self.client.get_most_recent_http_headers()
        print 'Header Time elapsed: %s' % header_time_elapsed
        print 'Time elapsed: %s' % time_elapsed
        return {'response': response,
                'time_elapsed': time_elapsed,
                'header_time_elapsed': header_time_elapsed}

    def _random_feature(self):
        point = (lat,lon) = self._random_US_lat_lon()
        properties_d = {"name": 'name_%s_%s' % (lat,lon)}
        feature = Feature(coordinates=point, properties=properties_d)
        return feature
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

