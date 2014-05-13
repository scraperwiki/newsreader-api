#!/usr/bin/env python
# encoding: utf-8
import json

from dshelpers import request_url


class SparqlQuery(object):
    """ Represents a general SPARQL query for the KnowledgeStore. """
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

    def get_total_result_count(self):
        pass


class EntitiesThatAreActorsQuery(SparqlQuery):
    """ Represents Query 3 in the Google Docs list of SPARQL queries. """
    def __init__(self, *args, **kwargs):
        super(EntitiesThatAreActorsQuery, self).__init__(*args, **kwargs)
        self.query_template = ("SELECT ?type (COUNT (*) as ?n) "
                               "WHERE "
                               "{{?a rdf:type sem:Actor . "
                               "?a rdf:type ?type . "
                               "FILTER (?type != sem:Actor)}} "
                               "GROUP BY ?type "
                               "ORDER BY DESC(?n) "
                               "OFFSET {offset} "
                               "LIMIT {limit}")
        self.query = self._make_query()

    def _make_query(self):
        """ Builds a query using template. """
        return self.query_template.format(offset=self.offset, limit=self.limit)
