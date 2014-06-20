#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals
import unittest

from nose.tools import assert_equal, assert_is_instance

from app import app

class SimpleAPITestCase(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.app = app.test_client()

    def test_root(self):
        rv = self.app.get('/')
        assert '<h2>NewsReader Simple API: Endpoints available at this location</h2>' in rv.data

    def test_actors_of_a_type(self):
        rv = self.app.get('/actors_of_a_type?uris.0=dbo:Person&filter=david')
        assert 'http://dbpedia.org/resource/David_Beckham' in rv.data.decode('UTF-8')

    def test_visit_a_non_existant_page(self):
        pass

    def test_visit_a_page_beyond_the_offset_limit(self):
        pass