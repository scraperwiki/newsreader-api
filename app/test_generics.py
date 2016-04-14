#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals
import unittest

from nose.tools import assert_equal

from app import app

import os
import mock
from mock import patch
import requests
from requests import ConnectionError

class SimpleAPIGenericTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        api_key = os.environ['NEWSREADER_PUBLIC_API_KEY'].split(',')[0]
        cls.app = app.test_client()
        cls.api_key_query_string = ('&api_key=' + api_key)

    def test_root(self):
        rv = self.app.get('/')
        assert '<h2>NewsReader Simple API: Endpoints available at this location</h2>' in rv.data
        
    def test_visit_a_non_existent_page(self):
        rv = self.app.get('/properties_of_a_type/page/14?uris.0=dbo%3AStadium' + self.api_key_query_string)
        print rv.data
        assert 'Result empty, possibly as a result of paging beyond results' in rv.data.decode('UTF-8')

    def test_visit_a_page_beyond_the_offset_limit(self):
        rv = self.app.get('/event_details_filtered_by_actor/page/501?uris.0=dbpedia%3AMartin_Winterkorn' + self.api_key_query_string)
        print rv.data
        assert 'OFFSET exceeds 10000, add filter or datefilter to narrow results' in rv.data.decode('UTF-8')

    def test_produce_jsonp_output(self):
        rv = self.app.get('/actors_of_a_type?uris.0=dbo:Person&filter=david&callback=mycallback' + self.api_key_query_string)
        assert_equal(rv.data[0:11], "mycallback(")
        assert_equal(rv.data[-2:],");")

    def test_handles_connection_error(self):
        with patch.object(requests, 'get') as mock_method:
            mock_method.side_effect = ConnectionError
            rv = self.app.get('/actors_of_a_type?uris.0=dbo:Person&filter=david&callback=mycallback' + self.api_key_query_string)
            assert_equal(rv.data, 'mycallback(Query raised an exception: ConnectionError);')
            #print rv.error_message

    def test_query_does_not_exist(self):
        rv = self.app.get('/bogus_query?uris.0=dbo:Person&filter=david&output=json' + self.api_key_query_string)
        assert_equal(rv.data, '{"error": "Query **bogus_query** does not exist"}')

    def test_cors_header(self):
        rv = self.app.get('/describe_uri?uris.0=dbpedia:Guangzhou_Evergrande_F.C.&output=json' + self.api_key_query_string)
        assert_equal(rv.headers['Access-Control-Allow-Origin'], '*')

    def test_handles_not_ok_response(self):
        with patch.object(requests, 'get') as mock_method:
            fake_response = mock.Mock()
            fake_response.status_code = 404
            mock_method.return_value = fake_response
            rv = self.app.get('/actors_of_a_type?uris.0=dbo:Person&filter=david&callback=mycallback' + self.api_key_query_string)
            assert_equal(rv.data, 'mycallback(Response code not OK: 404);')

    def test_handles_malformed_url(self):
        rv = self.app.get('/event_details_filtered_by_actor?uris.0=&!' + self.api_key_query_string)
        assert 'Query URL is malformed' in rv.data.decode('UTF-8')

    def test_handles_accents_in_urls(self):
        rv = self.app.get('/actors_of_a_type?uris.0=dbo:Person&filter=J%C3%BCrgen' + self.api_key_query_string)
        assert 'error' not in rv.data.decode('UTF-8')


class AuthenticationFailureTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = app.test_client()

    def test_does_not_allow_unauthorized_api_key(self):
        rv = self.app.get('/describe_uri?uris.0=dbpedia:Guangzhou_Evergrande_F.C.&output=json' + '&api_key=INVALID')
        assert_equal(401, rv.status_code)


class ApiKeysTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.public_api_key = os.environ['NEWSREADER_PUBLIC_API_KEY'].split(',')[0]
        cls.private_api_key = os.environ['NEWSREADER_PRIVATE_API_KEY'].split(',')[0]
        # If this isn't true, we're not properly testing the cases here.
        assert cls.public_api_key != cls.private_api_key

        cls.app = app.test_client()

    def test_public_api_key_allows_access_to_public_api(self):
        rv = self.app.get('/describe_uri?uris.0=dbpedia:Guangzhou_Evergrande_F.C.&output=json' + '&api_key='
                          + self.public_api_key)
        assert_equal(200, rv.status_code)

    def test_private_api_key_does_not_allow_access_to_public_api(self):
        rv = self.app.get('/describe_uri?uris.0=dbpedia:Guangzhou_Evergrande_F.C.&output=json' + '&api_key='
                          + self.private_api_key)
        assert_equal(401, rv.status_code)

    def test_private_api_key_allows_access_to_private_api(self):
        rv = self.app.get('/ft/describe_uri?uris.0=dbpedia:Guangzhou_Evergrande_F.C.&output=json' + '&api_key='
                          + self.private_api_key)
        assert_equal(200, rv.status_code)

    def test_public_api_key_does_not_allow_access_to_private_api(self):
        rv = self.app.get('/ft/describe_uri?uris.0=dbpedia:Guangzhou_Evergrande_F.C.&output=json' + '&api_key='
                          + self.public_api_key)
        assert_equal(401, rv.status_code)
