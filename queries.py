#!/usr/bin/env python
# encoding: utf-8


class SparqlQuery(object):
    def __init__(self, offset=0, limit=100):
        self.query_template = None
        self.json_result = None
        self.offset = offset
        self.limit = limit
        self.query = self._make_query()

    def _make_query(self):
        """ Builds a query using template,"""
        raise NotImplementedError

    def submit_query(self, endpoint_url='https://knowledgestore.fbk.eu'
                                        '/nwrdemo/sparql'):
        """ Submit query to endpoint; return result. """
