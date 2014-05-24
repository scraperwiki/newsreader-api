#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

import os
import json
import requests

from collections import namedtuple

from dshelpers import request_url

def convert_raw_json_to_clean(SPARQL_json):
    clean_json = []
    # This handles the describe_uri query
    if "results" not in SPARQL_json.keys():
      return SPARQL_json

    for entry in SPARQL_json['results']['bindings']:
        line = {}
        for key in entry.keys():
            line[key] = entry[key]['value']
        clean_json.append(line)
    return clean_json

class SparqlQuery(object):
    """ Represents a general SPARQL query for the KnowledgeStore. """
    def __init__(self, offset=0, limit=100, uris=None, filter=":", output='html'):
        self.offset = offset
        self.limit = limit
        self.filter = filter

        if uris is None:
            self.uris = []
        else:
            # SPARQL queries require URIs wrapped in <,>
            self.uris = ['<' + item + '>' for item in uris]

        self.query_title = None
        self.query_template = None
        self.query = None
        self.json_result = None
        self.clean_json = None
        self.output = output
        self.headers = []
        self.jinja_template = "default.html"

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

    def submit_query(self,
                     username=os.environ['NEWSREADER_USERNAME'],
                     password=os.environ['NEWSREADER_PASSWORD'],
                     endpoint_url='https://knowledgestore.fbk.eu'
                                  '/nwr/worldcup-hackathon/sparql'):
        """ Submit query to endpoint; return result. """
        payload = {'query': self.query}
        response = requests.get(endpoint_url, auth=(username, password),
                               params=payload)
        #response = request_url(endpoint_url, auth=(username, password),
        #                       params=payload,
        #                       back_off=True)
        
        self.json_result = json.loads(response.content)
        self.clean_json = convert_raw_json_to_clean(self.json_result)

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
        return int(self.json_result['results']['bindings'][0]['count']['value'])


class entities_that_are_actors(SparqlQuery):
    """ List entities that appear in any event, restricted to dbpedia

    http://127.0.0.1:5000/entities_that_are_actors?output=json&filter=player
    """
    def __init__(self, *args, **kwargs):
        super(entities_that_are_actors, self).__init__(*args, **kwargs)
        self.query_title = 'dbpedia entities that are actors in any event'
        self.query_template = ("SELECT ?type (COUNT (*) as ?count) "
                               "WHERE {{ "
                               "?a rdf:type sem:Actor . "
                               "?a rdf:type ?type . "
                               'FILTER (?type != sem:Actor && '
                               'STRSTARTS(STR(?type), '
                               '"http://dbpedia.org/ontology/") && '
                               'contains(LCASE(str(?type)), "{filter}"))}} '
                               "GROUP BY ?type "
                               "ORDER BY DESC(?count) "
                               "OFFSET {offset} "
                               "LIMIT {limit}")
        self.query = self._build_query()

        self.count_template = ('SELECT (COUNT (distinct ?type) as ?count) '
                               'WHERE {{ '
                               '?a rdf:type sem:Actor . '
                               '?a rdf:type ?type . '
                               'FILTER (?type != sem:Actor && '
                               'STRSTARTS(STR(?type), '
                               '"http://dbpedia.org/ontology/") && '
                               'contains(LCASE(str(?type)), "{filter}"))}}')

        self.jinja_template = 'two_column.html'
        self.headers = ['type','count']

    def _build_query(self):
        """ Returns a query string. """
        query = self.query_template.format(offset=self.offset, 
                                          limit=self.limit,
                                          filter=self.filter) 
        print query
        return query

    def _build_count_query(self):
        """ Returns a count query string. """
        return self.count_template.format(filter=self.filter)

    def get_total_result_count(self):
        """ Returns result count for query. """
        count_query = CountQuery(self._build_count_query())
        return count_query.get_count()

    def parse_query_results(self):
        # TODO: nicely parsed needs defining; may depend on query
        """ Returns nicely parsed result of query. """
        Query3Result = namedtuple('Query3Result', 'type count')
        # TODO: consider yielding results instead

        return [Query3Result(result['type']['value'], result['count']['value'])
                for result in self.json_result['results']['bindings']]


class GetEventDetailsByActorUri(SparqlQuery):
    """ Get event details involving a specified URI (limited to first 100) 

        http://127.0.0.1:5000/GetEventDetailsByActorUri?uris.0=http://dbpedia.org/resource/David_Beckham&output=json
    """
    def __init__(self, *args, **kwargs):
        super(GetEventDetailsByActorUri, self).__init__(*args, **kwargs)
        self.query_title = 'Get event details by actor URI'
        self.headers = ['event', 'predicate', 'object', 'object_type']
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
                               'SELECT (count(*) as ?count) '
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

        self.jinja_template = 'four_column.html'

    def _build_query(self):
        """ Returns a query string. """
        return self.query_template.format(offset=self.offset,
                                          limit=self.limit,
                                          uri_0=self.uris[0])

    def parse_query_results(self):
        """ Returns nicely parsed result of query. """
        Query13Result = namedtuple('Query13Result',
                                   'event predicate object object_type')
        # Not all results contain all entries
        return [Query13Result(result.get('event', {}).get('value'),
                              result.get('predicate', {}).get('value'),
                              result.get('object', {}).get('value'),
                              result.get('object_type', {}).get('value'))
                for result in self.json_result['results']['bindings']]

    def _build_count_query(self):
        """ Returns a count query string. """
        return self.count_template.format(uri_0=self.uris[0])

    def get_total_result_count(self):
        """ Returns result count for query. """
        count_query = CountQuery(self._build_count_query())
        return count_query.get_count()

class describe_uri(SparqlQuery):
    """ Details of a URI returned by the DESCRIBE query

        http://127.0.0.1:5000/describe_uri?uris.0=http://dbpedia.org/resource/David_Beckham&output=json
    """
    def __init__(self, *args, **kwargs):
        super(describe_uri, self).__init__(*args, **kwargs)
        self.query_title = 'Details of a URI returned by the DESCRIBE query'
        self.query_template = ("""
                               Describe {uri_0}
                               """)

        self.query = self._build_query()

        self.count_template = ("")

        self.jinja_template = 'default.html'

    def _build_query(self):
        """ Returns a query string. """
        return self.query_template.format(offset=self.offset,
                                          limit=self.limit,
                                          uri_0=self.uris[0])

    def _build_count_query(self):
        """ Returns a count query string. """
        return self.count_template

    def get_total_result_count(self):
        """ Returns result count for query, exception for this describe query """
        return 0

    def parse_query_results(self):
        # TODO: nicely parsed needs defining; may depend on query
        """ Returns nicely parsed result of query. """
        return self.json_result

class actors_of_a_type(SparqlQuery):
    """ Get actors, counts and comments for actors with a specified type  

    http://127.0.0.1:5000/actors_of_a_type?uris.0=http://dbpedia.org/ontology/Person&output=json&filter=david
    """
    def __init__(self, *args, **kwargs):
        super(actors_of_a_type, self).__init__(*args, **kwargs)
        self.query_title = 'Get URIs, counts and comments of actors with a specified type'
        self.query_template = ("""
                                SELECT ?actor (count(?actor) as ?count) ?comment
                                WHERE {{ 
                                ?event rdf:type sem:Event . 
                                ?event sem:hasActor ?actor .
                                ?actor rdf:type {uri_0} .
                                OPTIONAL {{?actor rdfs:comment ?comment .}}
                                #FILTER (contains(LCASE(str(?actor)), "{filter}")) .
                                }}
                                GROUP BY ?actor ?comment
                                ORDER BY desc(?n)
                                OFFSET {offset}
                                LIMIT {limit}
                               """)
        self.query = self._build_query()

        self.count_template = ("""
                                SELECT (count(DISTINCT ?actor) as ?count)
                                WHERE {{ 
                                ?event rdf:type sem:Event . 
                                ?event sem:hasActor ?actor .
                                ?actor rdf:type {uri_0} .
                                OPTIONAL {{?actor rdfs:comment ?comment .}}
                                #FILTER (contains(LCASE(str(?actor)), "{filter}")) .
                                }}
                               """)

        self.jinja_template = 'three_column.html'
        self.headers = ['actor','count','comment']

    def _build_query(self):
        """ Returns a query string. """
        query = self.query_template.format(offset=self.offset, 
                                          limit=self.limit,
                                          filter=self.filter,
                                          uri_0=self.uris[0]) 
        print query
        return query

    def _build_count_query(self):
        """ Returns a count query string. """
        return self.count_template.format(filter=self.filter, 
                                          uri_0=self.uris[0])

    def get_total_result_count(self):
        """ Returns result count for query. """
        count_query = CountQuery(self._build_count_query())
        return count_query.get_count()

    def parse_query_results(self):
        # TODO: nicely parsed needs defining; may depend on query
        """ Returns nicely parsed result of query. """
        Query3Result = namedtuple('Query3Result', 'actor count comment')
        # TODO: consider yielding results instead
        print self.json_result
        return [Query3Result(result['actor']['value'], 
                             result['count']['value'],
                             result['comment']['value'],)
                for result in self.json_result['results']['bindings']]

