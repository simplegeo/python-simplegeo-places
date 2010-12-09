#!/usr/bin/env python

import random
import time
import numpy
import math

from simplegeo.places import Client
from simplegeo.shared import Feature, APIError

MY_OAUTH_KEY = ''
MY_OAUTH_SECRET = ''

API_VERSION = '1.0'
API_HOST = ''
#API_HOST = 'api.simplegeo.com'
API_PORT = 80

class Statistic(object):
    """
    Hookin' it up with the seven descriptive statistics.
    """

    def __init__(self, sample):
        self.sample = sample

    def size(self):
        return len(self.sample)

    def min(self):
        return min(self.sample)

    def max(self):
        return max(self.sample)

    def mean(self):
        return sum(self.sample) / len(self.sample)

    def median(self):
        length = len(self.sample)
        if length % 2 == 0:
            return (self.sample[length/2] + self.sample[length/2 + 1]) / 2
        else:
            return self.sample[int(math.floor(length/2))]
            
    def variance(self):
        mean = self.mean()
        return sum(math.pow(mean - value, 2) for value in self.sample) / (len(self.sample)-1)

    def standard_deviation(self):
        return math.sqrt(self.variance())

    def histogram(self, width=80.0):
        k = int(math.ceil(math.sqrt(self.size())))
        size = (self.max() - self.min()) / k
        bins = [(self.min() + (i * size), (self.min() + (i + 1) * size)) for i in xrange(k)]
        labels = ['%8.5f - %8.5f [%%s]' % bin for bin in bins]
        labelsize = max(len(label) for label in labels)
        populations = [len([i for i in self.sample if bin[0] <= i < bin[1]]) for bin in bins]
        maxpop = max(populations)
        histosize = width - labelsize - 1
        width = width - len(str(maxpop)) - 1
        for i, label in enumerate(labels):
            label = label % str(populations[i]).rjust(len(str(maxpop)))
            print label.rjust(labelsize), '#' * int(populations[i] * width / float(maxpop))

class PerformanceTest(object):
    def __init__(self, number_of_requests=10):
        self.number_of_requests = number_of_requests
        self.client = Client(MY_OAUTH_KEY, MY_OAUTH_SECRET, API_VERSION, API_HOST, API_PORT)
        self.responses = []
        self.request_test = { 'add_feature': self._timed_response_add_feature,
                         'get_feature': self._timed_response_get_feature,
                         'update_feature': self._timed_response_update_feature,
                         'delete_feature': self._timed_response_delete_feature,
                         'search': self._timed_response_search}
        self.simplegeoids =[]

    def run(self):
        self.performance_test('add_feature')
        time.sleep(20)
        self.responses = []
        self.performance_test('get_feature')
        self.responses = []
        self.performance_test('update_feature')
        self.responses = []        
        self.performance_test('search')
        self.responses = []
        self.performance_test('delete_feature')

    def performance_test(self, request_type):
        requests_completed = 0 
        requests_failed = 0 

        for i in range(self.number_of_requests):
            try:
                ###print '\n\nTrying %s request %s\n\n' % (request_type,i) 
                timed_response = self._timed_response(request_type)
                requests_completed += 1
                self.responses.append(timed_response)
                #time.sleep(1)
            except APIError,ex:
                print ex
                requests_failed += 1
     
        ###print '\n\n', self.responses
        print '\n\n%s %s requests completed, %s requests failed' % (requests_completed, request_type, requests_failed)
        
        self._create_ghettogram([response['time_elapsed'] for response in self.responses])
        self._create_ghettogram([response['header_time_elapsed']/1000.0 for response in self.responses if response['header_time_elapsed'] is not None])
        
        
    def _create_ghettogram(self, times):
        
        statistic = Statistic(times)
        print '\n\nmean: %s, variance is: %s, min: %s, max: %s median: %s' % (statistic.mean(), statistic.variance(), statistic.min(), statistic.max(), statistic.median())
        print '+1 deviation (68%%): %s' % (statistic.mean() + statistic.standard_deviation())
        print '+2 deviation (95%%): %s' % (statistic.mean() + statistic.standard_deviation() * 2)
        print '+3 deviation (99%%): %s' % (statistic.mean() + statistic.standard_deviation() * 3)
        statistic.histogram()

    def _timed_response(self, request_type):
        return self.request_test[request_type]()

    def _timed_response_add_feature(self):
        feature = self._random_feature()
        print 'Timing: client.add_feature(%s)' % (feature.to_dict())
        start_time = time.time()
        response = self.client.add_feature(feature)
        time_elapsed = time.time() - start_time
        #print 'Headers: %s\n\n' % self.client.get_most_recent_http_headers()
        try:
            header_time_elapsed = float(self.client.get_most_recent_http_headers()['x-response-time'].rstrip('ms'))
        except KeyError:
            header_time_elapsed = None
        ###print 'Header Time elapsed: %s' % header_time_elapsed
        ###print 'Time elapsed: %s' % time_elapsed
        self.simplegeoids.append(response);
        return {'feature': feature.to_dict(),
                'response': response,
                'time_elapsed': time_elapsed,
                'header_time_elapsed': header_time_elapsed}

    def _timed_response_get_feature(self):
        sgid = self._random_simplegeoid()
        print 'Timing: client.get_feature(%s)' % sgid
        start_time = time.time()
        response = self.client.get_feature(sgid)
        time_elapsed = time.time() - start_time
        #print 'Headers: %s\n\n' % self.client.get_most_recent_http_headers()
        try:
            header_time_elapsed = float(self.client.get_most_recent_http_headers()['x-response-time'].rstrip('ms'))
        except KeyError:
            header_time_elapsed = None
        ###print 'Header Time elapsed: %s' % header_time_elapsed
        ###print 'Time elapsed: %s' % time_elapsed
        return {'sgid': sgid,
                'response': response,
                'time_elapsed': time_elapsed,
                'header_time_elapsed': header_time_elapsed}

    def _timed_response_update_feature(self):
        sgid = self._random_simplegeoid()
        feature = self.client.get_feature(sgid)
        print 'Timing: client.update_feature(%s,%s)' % (sgid, feature.to_dict())
        #changing the lat/lon to make it a *real* update
        (feature.lat,feature.lon) = self._random_US_lat_lon()
        start_time = time.time()
        response = self.client.update_feature(feature)
        time_elapsed = time.time() - start_time
        #print 'Headers: %s\n\n' % self.client.get_most_recent_http_headers()
        try:
            header_time_elapsed = float(self.client.get_most_recent_http_headers()['x-response-time'].rstrip('ms'))
        except KeyError:
            header_time_elapsed = None
        ###print 'Header Time elapsed: %s' % header_time_elapsed
        ###print 'Time elapsed: %s' % time_elapsed
        return {'sgid': sgid,
                'feature': feature.to_dict(),
                'response': response,
                'time_elapsed': time_elapsed,
                'header_time_elapsed': header_time_elapsed}

    def _timed_response_delete_feature(self):
        sgid = self._random_simplegeoid()
        self.simplegeoids.remove(sgid)
        print 'Timing: client.delete_feature(%s)' % sgid
        start_time = time.time()
        response = self.client.delete_feature(sgid)
        time_elapsed = time.time() - start_time
        #print 'Headers: %s\n\n' % self.client.get_most_recent_http_headers()
        try:
            header_time_elapsed = float(self.client.get_most_recent_http_headers()['x-response-time'].rstrip('ms'))
        except KeyError:
            header_time_elapsed = None
        ###print 'Header Time elapsed: %s' % header_time_elapsed
        ###print 'Time elapsed: %s' % time_elapsed
        return {'sgid': sgid,
                'response': response,
                'time_elapsed': time_elapsed,
                'header_time_elapsed': header_time_elapsed}

    def _timed_response_search(self):
        (lat,lon) = self._random_US_lat_lon()
        print 'Timing: client.search(%s,%s,%s)' % (lat,lon,'restaurant')
        start_time = time.time()
        response = self.client.search(lat,lon,query='',category='restaurant')
        time_elapsed = time.time() - start_time
        ########self.simplegeoids.extend([feat.id for feat in response])
        #print 'Headers: %s\n\n' % self.client.get_most_recent_http_headers()
        try:
            header_time_elapsed = float(self.client.get_most_recent_http_headers()['x-response-time'].rstrip('ms'))
        except KeyError:
            header_time_elapsed = None
        ###print 'Header Time elapsed: %s' % header_time_elapsed
        ###print 'Time elapsed: %s' % time_elapsed
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

