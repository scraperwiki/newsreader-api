#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals
import unittest

import json

from nose.tools import assert_equal, assert_is_instance, assert_raises

import mock
from mock import patch
import requests
from requests import ConnectionError, RequestException

from app import app
import queries

#TODO
# Test handling of following errors:
# 1. Query does not exist - AttributeError
# 2. Query not parsable/ arguments malformed


class SimpleAPIGenericTests(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.app = app.test_client()

    def test_visit_a_non_existent_page(self):
        rv = self.app.get('/properties_of_a_type/page/3?uris.0=dbo%3AStadium')
        assert_equal(rv.data, 'Result empty, possibly as a result of paging beyond results')

    def test_visit_a_page_beyond_the_offset_limit(self):
        rv = self.app.get('/event_details_filtered_by_actor/page/501?uris.0=dbpedia:David_Beckham')
        assert_equal(rv.data, 'OFFSET exceeds 10000, add filter or datefilter to narrow results')

    def test_produce_jsonp_output(self):
        rv = self.app.get('/actors_of_a_type?uris.0=dbo:Person&filter=david&callback=mycallback')
        assert_equal(rv.data[0:11], "mycallback(")
        assert_equal(rv.data[-2:],");")

    def test_handles_connection_error(self):
        with patch.object(requests, 'get') as mock_method:
            mock_method.side_effect = ConnectionError
            rv = self.app.get('/actors_of_a_type?uris.0=dbo:Person&filter=david&callback=mycallback')
            assert_equal(rv.data, 'Query raised an exception: ConnectionError')
            #print rv.error_message

    def test_query_does_not_exist(self):
        rv = self.app.get('/bogus_query?uris.0=dbo:Person&filter=david&callback=mycallback')
        assert_equal(rv.data, 'Query "bogus_query" does not exist')        

    def test_handles_not_ok_response(self):
        with patch.object(requests, 'get') as mock_method:
            fake_response = mock.Mock()
            fake_response.status_code = 404
            mock_method.return_value = fake_response
            rv = self.app.get('/actors_of_a_type?uris.0=dbo:Person&filter=david&callback=mycallback')
            assert_equal(rv.data, 'Response code not OK: 404')

class SimpleAPIQueryTests(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.app = app.test_client()

    def test_root(self):
        rv = self.app.get('/')
        assert '<h2>NewsReader Simple API: Endpoints available at this location</h2>' in rv.data

    def test_actors_of_a_type(self):
        rv = self.app.get('/actors_of_a_type?uris.0=dbo:Person&filter=david')
        assert 'http://dbpedia.org/resource/David_Beckham' in rv.data.decode('UTF-8')

    def test_describe_uri(self):
        rv = self.app.get('/describe_uri?uris.0=dbpedia:Guangzhou_Evergrande_F.C.&output=json')
        assert "dbpedia:Category:1954_establishments_in_China" in rv.data.decode('UTF-8')

    def test_event_details_filtered_by_actor(self):
        rv = self.app.get('/event_details_filtered_by_actor?uris.0=dbpedia:David_Beckham')
        assert 'http://www.theguardian.com/uk/2010/dec/01/england-world-cup-putin-refusal#effortEvent' in rv.data.decode('UTF-8')  

    def test_event_label_frequency_count(self):
        rv = self.app.get('/event_label_frequency_count?filter=bribe+OR+bribery')
        assert '1521' in rv.data.decode('UTF-8')

    def test_get_document(self):
        rv = self.app.get('/get_document?uris.0=http://news.bbc.co.uk/sport2/hi/football/gossip_and_transfers/5137822.stm')
        data = json.loads(rv.data)
        assert_equal(len(data['payload']['content']), 5872)

    def test_get_document_metadata(self):
        rv = self.app.get('/get_document_metadata?uris.0=http://news.bbc.co.uk/sport2/hi/football/gossip_and_transfers/5137822.stm')
        assert 'ks:hasMention' in rv.data.decode('UTF-8')

    def test_get_mention_metadata(self):
        rv = self.app.get('/get_mention_metadata?uris.0=http%3A%2F%2Fnews.bbc.co.uk%2Fsport2%2Fhi%2Ffootball%2Fgossip_and_transfers%2F5137822.stm%23char%3D1162%2C1167%26word%3Dw220%26term%3Dt220')
        assert 'framenet:Statement' in rv.data.decode('UTF-8')

    def test_people_sharing_event_with_a_person(self):
        rv = self.app.get('/people_sharing_event_with_a_person?uris.0=dbpedia:David_Beckham')
        assert 'http://dbpedia.org/resource/Sven-Göran_Eriksson' in rv.data.decode('UTF-8')

    def test_properties_of_a_type(self):
        rv = self.app.get('/properties_of_a_type?uris.0=dbo:Stadium')
        assert 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type' in rv.data.decode('UTF-8')

    def test_property_of_actors_of_a_type(self):
        rv = self.app.get('/property_of_actors_of_a_type?uris.1=dbo:height&filter=david&uris.0=dbo:SoccerPlayer')
        assert '1.9304' in rv.data.decode('UTF-8')
        
    def test_summary_of_events_with_actor(self):
        rv = self.app.get('/summary_of_events_with_actor?uris.0=dbpedia:Thierry_Henry')
        assert '4055' in rv.data.decode('UTF-8')

    def test_summary_of_events_with_actor_type(self):
        rv = self.app.get('/summary_of_events_with_actor_type?datefilter=2010-01&uris.0=dbo:GolfPlayer')
        assert 'http://dbpedia.org/resource/Colin_Montgomerie' in rv.data.decode('UTF-8')

    def test_summary_of_events_with_event_label(self):
        rv = self.app.get('/summary_of_events_with_event_label?filter=bribe&datefilter=2010')
        assert 'bribe' in rv.data.decode('UTF-8')

    def test_summary_of_events_with_framenet(self):
        rv = self.app.get('/summary_of_events_with_framenet?uris.0=framenet:Omen')
        assert '2004-03-08' in rv.data.decode('UTF-8')

    def test_summary_of_events_with_two_actors(self):
        rv = self.app.get('/summary_of_events_with_two_actors?uris.0=dbpedia:David_Beckham&uris.1=dbpedia:Sepp_Blatter')
        assert 'http://www.newsreader-project.eu/LNdata/hackathon/2004/03/01/4BTY-GSF0-01G8-73BK.xml#sayEvent' in rv.data.decode('UTF-8')

    def test_types_of_actors(self):
        try:
            rv = self.app.get('/types_of_actors?filter=player')
            assert 'http://dbpedia.org/ontology/GridironFootballPlayer' in rv.data.decode('UTF-8')
        except Exception as e:
            print type(e)
            print e.message
        

   
