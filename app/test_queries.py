#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals
import json
import unittest

import dshelpers
import mock
import queries

from nose.tools import assert_equal, assert_is_instance


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


class SparqlQuerySubmitQueryTestCase(unittest.TestCase):
    @mock.patch('app.queries.request_url')
    def setUp(self, mock_request_url):
        fake_response = mock.Mock()
        fake_response.content = '{"test": "ok"}'
        mock_request_url.return_value = fake_response
        self.mock_request_url = mock_request_url

        self.query = queries.SparqlQuery()
        self.query.submit_query()

    def test_result_from_submit_query(self):
        expected_json_result = {u'test': u'ok'}
        assert_equal(expected_json_result, self.query.json_result)

    def test_request_url_call_from_submit_query(self):
        endpoint_url = 'https://knowledgestore.fbk.eu/nwrdemo/sparql'
        payload = {'query': self.query.query}
        self.mock_request_url.assert_called_with(endpoint_url, params=payload)


class CountQueryTestCase(unittest.TestCase):
    # TODO: implement some tests
    pass


class EntitiesThatAreActorsQuery(unittest.TestCase):
    # TODO: implement some tests
    pass
