#!/usr/bin/env python
# encoding: utf-8
import json

from dshelpers import request_url


class SparqlQuery(object):
    def __init__(self, offset=0, limit=100):
        self.query_template = None
        self.json_result = None
        self.offset = offset
        self.limit = limit
        self.query = None

    def _make_query(self):
        """ Builds a query using template. """
        # TODO: consider making default here needs to insert offset and limit
        raise NotImplementedError

    def submit_query(self, endpoint_url='https://knowledgestore.fbk.eu'
                                        '/nwrdemo/sparql'):
        """ Submit query to endpoint; return result. """
        payload = {'query': self.query}
        response = request_url(endpoint_url, params=payload)
        return json.loads(response.content)
