#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

import json

from collections import namedtuple

from dshelpers import request_url


class SparqlQuery(object):
    """ Represents a general SPARQL query for the KnowledgeStore. """
    def __init__(self, offset=0, limit=100, uris=None):
        self.offset = offset
        self.limit = limit

        if uris is None:
            self.uris = []
        else:
            self.uris = uris

        self.query_title = None
        self.query_template = None
        self.query = None
        self.json_result = None

    def _build_query(self):
        """ Implement in child classes. """
        # TODO: Consider making return self.query_template
        # so we could then have self.query = self._build_query()
        raise NotImplementedError("Should be implemented in child class.")

    def _build_count_query(self):
        # TODO: Consider making return self.count_template
        # and making self.count_template = None
        """ Implement in child classes. """
        raise NotImplementedError("Should be implemented in child class.")

    def submit_query(self, endpoint_url='https://knowledgestore.fbk.eu'
                                        '/nwrdemo/sparql'):
        """ Submit query to endpoint; return result. """
        payload = {'query': self.query}
        response = request_url(endpoint_url, params=payload)
        self.json_result = json.loads(response.content)

    def parse_query_results(self):
        """ Implement in child classes. """
        raise NotImplementedError("Should be implemented in child class.")

    def get_total_result_count(self):
        """ Implement in child classes. """
        raise NotImplementedError("Should be implemented in child class.")


class CountQuery(SparqlQuery):
    """
    Represents a general count SPARQL query for the KnowledgeStore.

    Uses the count_template in a SPARQL query to create appropriate CountQuery.
    """
    # TODO: is *args, **kwargs really needed here?
    def __init__(self, count_query, *args, **kwargs):
        super(CountQuery, self).__init__(*args, **kwargs)
        self.query_title = 'Count query'
        self.query_template = count_query
        self.query = self._build_query()

    def _build_query(self):
        """ Returns a query string. """
        return self.query_template

    # TODO: Should get_count() be the more general parse_query_results()?
    def get_count(self):
        """ Parses and returns result from a count query. """
        self.submit_query()
        return int(self.json_result['results']['bindings'][0]['n']['value'])


class EntitiesThatAreActorsQuery(SparqlQuery):
    """ Represents Query 3 in the Google Docs list of SPARQL queries. """
    def __init__(self, *args, **kwargs):
        super(EntitiesThatAreActorsQuery, self).__init__(*args, **kwargs)
        self.query_title = 'Query 3; entities that are actors'
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

    def parse_query_results(self):
        # TODO: nicely parsed needs defining; may depend on query
        """ Returns nicely parsed result of query. """
        Query3Result = namedtuple('Query3Result', 'entity_type count')
        # TODO: consider yielding results instead
        return [Query3Result(result['type']['value'], result['n']['value'])
                for result in self.json_result['results']['bindings']]


class SynerscopeQuery(SparqlQuery):
    """ Represents the Synerscope query (query 13) in the list. """
    def __init__(self, *args, **kwargs):
        super(SynerscopeQuery, self).__init__(*args, **kwargs)
        self.query_title = 'Query 13; Synerscope query'
        self.query_template = ('PREFIX sem: <http://semanticweb.cs.vu.nl/'
                               '2009/11/sem/> '
                               'SELECT ?event ?predicate ?object '
                               '?object_type '
                               'WHERE {{ '
                               '?event ?predicate ?object . '
                               'OPTIONAL '
                               '{{ '
                               '?object a ?object_type . '
                               'FILTER(STRSTARTS(STR(?object_type), '
                               '"http://semanticweb.cs.vu.nl/2009/11/sem/"))'
                               '}} {{ '
                               'SELECT ?event '
                               'WHERE {{ '
                               '?event a sem:Event .'
                               '?event sem:hasActor {uri_0} .'
                               '}} '
                               'LIMIT 100 '
                               'OFFSET 0 '
                               '}} }} '
                               'ORDER BY DESC(?event) '
                               'LIMIT {limit} '
                               'OFFSET {offset} ')

        self.query = self._build_query()

        self.count_template = ('PREFIX sem: <http://semanticweb.cs.vu.nl/'
                               '2009/11/sem/> '
                               'SELECT (count(*) as ?n) '
                               'WHERE {{ '
                               '?event ?predicate ?object . '
                               'OPTIONAL '
                               '{{ '
                               '?object a ?object_type . '
                               'FILTER(STRSTARTS(STR(?object_type), '
                               '"http://semanticweb.cs.vu.nl/2009/11/sem/"))'
                               '}} {{ '
                               'SELECT ?event '
                               'WHERE {{ '
                               '?event a sem:Event .'
                               '?event sem:hasActor {uri_0} .'
                               '}} '
                               'LIMIT 100 '
                               'OFFSET 0 '
                               '}} }}')

    def _build_query(self):
        """ Returns a query string. """
        return self.query_template.format(offset=self.offset,
                                          limit=self.limit,
                                          uri_0=self.uris[0])

    def parse_query_results(self):
        """ Returns nicely parsed result of query. """
        Query13Result = namedtuple('Query13Result',
                                   'event predicate object object_type')
        return [Query13Result(result['event']['value'],
                              result['predicate']['value'],
                              result['object']['value'],
                              result['object_type']['value'])
                for result in self.json_result['results']['bindings'][0]]
