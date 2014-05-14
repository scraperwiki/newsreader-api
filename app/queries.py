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
        self.json_result = None

    def _build_query(self):
        """ Implement in child classes. """
        # TODO: Consider making return self.query_template
        # so we could then have self.query = self._build_query()
        raise NotImplementedError

    def _build_count_query(self):
        # TODO: Consider making return self.count_template
        # and making self.count_template = None
        """ Implement in child classes. """
        raise NotImplementedError

    def submit_query(self, endpoint_url='https://knowledgestore.fbk.eu'
                                        '/nwrdemo/sparql'):
        """ Submit query to endpoint; return result. """
        payload = {'query': self.query}
        response = request_url(endpoint_url, params=payload)
        self.json_result = json.loads(response.content)

    def get_total_result_count(self):
        """ Implement in child classes. """
        raise NotImplementedError


class CountQuery(SparqlQuery):
    """
    Represents a general count SPARQL query for the KnowledgeStore.

    Uses the count_template in a SPARQL query to create appropriate CountQuery.
    """
    # TODO: is *args, **kwargs really needed here?
    def __init__(self, count_query, *args, **kwargs):
        super(CountQuery, self).__init__(*args, **kwargs)
        self.query_template = count_query
        self.query = self._build_query()

    def _build_query(self):
        """ Returns a query string. """
        return self.query_template

    def get_count(self):
        """ Parses and returns result from a count query. """
        self.submit_query()
        return int(self.json_result['results']['bindings'][0]['n']['value'])


class EntitiesThatAreActorsQuery(SparqlQuery):
    """ Represents Query 3 in the Google Docs list of SPARQL queries. """
    def __init__(self, *args, **kwargs):
        super(EntitiesThatAreActorsQuery, self).__init__(*args, **kwargs)
        self.query_template = ("SELECT ?type (COUNT (*) as ?n) "
                               "WHERE "
                               "{{?a rdf:type sem:Actor . "
                               "?a rdf:type ?type . "
                               'FILTER (?type != sem:Actor && '
                               'STRSTARTS(STR(?type), '
                               '"http://dbpedia.org/ontology/"))}} '
                               "GROUP BY ?type "
                               "ORDER BY DESC(?n) "
                               "OFFSET {offset} "
                               "LIMIT {limit}")
        self.query = self._build_query()

        self.count_template = ('SELECT (COUNT (distinct ?type) as ?n) '
                               'WHERE { '
                               '?a rdf:type sem:Actor . '
                               '?a rdf:type ?type . '
                               'FILTER (?type != sem:Actor && '
                               'STRSTARTS(STR(?type), '
                               '"http://dbpedia.org/ontology/"))}')

    def _build_query(self):
        """ Returns a query string. """
        return self.query_template.format(offset=self.offset, limit=self.limit)

    def _build_count_query(self):
        """ Returns a count query string. """
        return self.count_template

    def get_total_result_count(self):
        """ Returns result count for query. """
        count_query = CountQuery(self._build_count_query())
        return count_query.get_count()
