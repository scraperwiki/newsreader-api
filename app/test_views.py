#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals
import unittest

import json

from nose.tools import assert_equal

import mock
from mock import patch
import requests
from requests import ConnectionError

from app import app

#TODO

class SimpleAPIQueryTests(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.app = app.test_client()

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
        rv = self.app.get('/types_of_actors?filter=player')
        assert 'http://dbpedia.org/ontology/GridironFootballPlayer' in rv.data.decode('UTF-8')

class CountTests(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.app = app.test_client()

    def test_1_actors_of_a_type(self):
        rv = self.app.get('/actors_of_a_type?uris.0=dbo:Person&filter=david&output=json')
        json_form = json.loads(rv.data)
        assert_equal(json_form['count'], 520)

    def test_2_describe_uri(self):
        rv = self.app.get('/describe_uri?uris.0=dbpedia:Guangzhou_Evergrande_F.C.&output=json')
        json_form = json.loads(rv.data)
        assert_equal(json_form['count'], 0)

    def test_3_event_details_filtered_by_actor(self):
        rv = self.app.get('/event_details_filtered_by_actor?uris.0=dbpedia:Zinedine_Zidane&output=json')
        json_form = json.loads(rv.data)
        assert_equal(json_form['count'],6440)  

    def test_4_event_label_frequency_count(self):
        rv = self.app.get('/event_label_frequency_count?filter=bribe+OR+bribery&output=json')
        json_form = json.loads(rv.data)
        assert_equal(json_form['count'], 78)

    def test_5_get_document(self):
        rv = self.app.get('/get_document?uris.0=http://news.bbc.co.uk/sport2/hi/football/gossip_and_transfers/5137822.stm')
        json_form = json.loads(rv.data)
        assert_equal(json_form['count'], 0)

    def test_6_get_document_metadata(self):
        rv = self.app.get('/get_document_metadata?uris.0=http://news.bbc.co.uk/sport2/hi/football/gossip_and_transfers/5137822.stm')
        json_form = json.loads(rv.data)
        assert_equal(json_form['count'], 0)

    def test_7_get_mention_metadata(self):
        rv = self.app.get('/get_mention_metadata?uris.0=http%3A%2F%2Fnews.bbc.co.uk%2Fsport2%2Fhi%2Ffootball%2Fgossip_and_transfers%2F5137822.stm%23char%3D1162%2C1167%26word%3Dw220%26term%3Dt220')
        json_form = json.loads(rv.data)
        assert_equal(json_form['count'], 0)

    def test_8_people_sharing_event_with_a_person(self):
        rv = self.app.get('/people_sharing_event_with_a_person?uris.0=dbpedia:David_Beckham&output=json')
        json_form = json.loads(rv.data)
        assert_equal(json_form['count'], 2866)

    def test_9_properties_of_a_type(self):
        rv = self.app.get('/properties_of_a_type?uris.0=dbo:Stadium&output=json')
        json_form = json.loads(rv.data)
        assert_equal(json_form['count'], 36)

    def test_10_property_of_actors_of_a_type(self):
        rv = self.app.get('/property_of_actors_of_a_type?uris.1=dbo:height&filter=david&uris.0=dbo:SoccerPlayer&output=json')
        json_form = json.loads(rv.data)
        assert_equal(json_form['count'], 58)
        
    def test_11_summary_of_events_with_actor(self):
        rv = self.app.get('/summary_of_events_with_actor?uris.0=dbpedia:Thierry_Henry&output=json')
        json_form = json.loads(rv.data)
        assert_equal(json_form['count'], 4059)

    def test_12_summary_of_events_with_actor_type(self):
        rv = self.app.get('/summary_of_events_with_actor_type?datefilter=2010-01&uris.0=dbo:GolfPlayer&output=json')
        json_form = json.loads(rv.data)
        assert_equal(json_form['count'], 88)

    def test_13_summary_of_events_with_event_label(self):
        rv = self.app.get('/summary_of_events_with_event_label?filter=bribe&datefilter=2010&output=json')
        json_form = json.loads(rv.data)
        assert_equal(json_form['count'], 317)

    def test_14_summary_of_events_with_framenet(self):
        rv = self.app.get('/summary_of_events_with_framenet?uris.0=framenet:Omen&output=json')
        json_form = json.loads(rv.data)
        assert_equal(json_form['count'], 15)

    def test_15_summary_of_events_with_two_actors(self):
        rv = self.app.get('/summary_of_events_with_two_actors?uris.0=dbpedia:David_Beckham&uris.1=dbpedia:Sepp_Blatter&output=json')
        json_form = json.loads(rv.data)
        assert_equal(json_form['count'], 331)

    def test_16_types_of_actors(self):
        rv = self.app.get('/types_of_actors?filter=player&output=json')
        json_form = json.loads(rv.data)
        assert_equal(json_form['count'], 22)  

   
