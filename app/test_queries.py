#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals
import unittest

from mock import patch
import requests
from requests import ConnectionError
import queries

from nose.tools import assert_equal, assert_is_instance, assert_raises


class SparqlQuerySetupTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.query = queries.SparqlQuery()

    def test_query_object_type(self):
        assert_is_instance(self.query, queries.SparqlQuery)

    def test_query_default_offset(self):
        assert_equal(0, self.query.offset)

    def test_query_default_limit(self):
        assert_equal(100, self.query.limit)

    def test_query_default_template(self):
        assert_equal(None, self.query.query_template)

    def test_query_default_query(self):
        assert_equal(None, self.query.query_template)

    def test_query_default_json_result(self):
        assert_equal(None, self.query.json_result)

    def test_uri_expander(self):
        input_uris = ['dbo:Person', 'dbpedia:Guangzhou_Evergrande_F.C.']
        expected_output = ['<http://dbpedia.org/ontology/Person>',
                           '<http://dbpedia.org/resource/Guangzhou_Evergrande_F.C.>']
        self.query._process_input_uris(input_uris)
        assert_equal(self.query.uris,expected_output)

class SparqlQuerySubmitQueryTestCase(unittest.TestCase):
    def test_response_to_connection_error(self):
        with patch.object(requests, 'get') as mock_method:
            with assert_raises(queries.QueryException) as qe:
                mock_method.side_effect = ConnectionError
                self.query = queries.SparqlQuery()
                self.query.submit_query('mock_username', 'mock_password')
