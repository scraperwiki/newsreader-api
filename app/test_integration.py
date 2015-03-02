#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals

import os

from app import app
from app import make_documentation

def test_generator():
    root_url = ""
    endpoint_path = '/cars'
    api_key = os.environ['NEWSREADER_SIMPLE_API_KEY']
    function_list = make_documentation.CarsDocsCreator(root_url, api_key,
                                                       endpoint_path).make_docs()
    for query in function_list['queries']:
        yield check_query, query['example']

def check_query(query):
    router = app.test_client()
    rv = router.get(query)
    assert 'error' not in rv.data.decode('UTF-8')

# This is how we tested counts
# def test_13_summary_of_events_with_event_label(self):
#        rv = self.app.get('/summary_of_events_with_event_label?filter=bribe&datefilter=2010&output=json')
#        json_form = json.loads(rv.data)
#        assert_equal(json_form['count'], 317)
