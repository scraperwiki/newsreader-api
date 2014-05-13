#!/usr/bin/env python
# encoding: utf-8
import json

from dshelpers import request_url


class SparqlQuery(object):
    """ Represents a general SPARQL query for the KnowledgeStore. """
    def __init__(self, offset=0, limit=100):
        self.offset = offset
        self.limit = limit

        self.query_template = None
        self.query = None
        self.total_result_count = None
        self.json_result = None

    def _build_query(self):
        """ Implement in child classes. """
        raise NotImplementedError

    def submit_query(self, endpoint_url='https://knowledgestore.fbk.eu'
                                        '/nwrdemo/sparql'):
        """ Submit query to endpoint; return result. """
        payload = {'query': self.query}
        response = request_url(endpoint_url, params=payload)
        return json.loads(response.content)

    def get_total_result_count(self):
        """ Gets result count for query. """
        raise NotImplementedError


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
        self.query = self._build_query()
        self.total_result_count = self.get_total_result_count()
        self.json_result = self.submit_query()

    def _build_query(self):
        """ Builds a query using template. """
        return self.query_template.format(offset=self.offset, limit=self.limit)

    def get_total_result_count(self):
        # TODO: implement
        pass
