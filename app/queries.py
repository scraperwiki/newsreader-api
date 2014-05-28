#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

import os
import json

from collections import namedtuple

from dshelpers import request_url

import requests
import requests_cache

import time

requests_cache.install_cache('requests_cache')


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

    def __init__(self, offset=0, limit=100, uris=None, output='html',
                 datefilter=None,
                 filter=":"):

        self.offset = offset
        self.limit = limit
        self.filter = filter
        self.datefilter = str(datefilter)
        self.date_filter_block = None
        self.original_uris = uris

        self._process_input_uris(uris)
        self._make_date_filter_block()

        self.query_title = None
        self.query_template = None
        self.query = None
        self.json_result = None
        self.clean_json = None
        self.output = output
        self.headers = []
        self.result_is_tabular = True
        self.jinja_template = "default.html"

        self.error_message = []
        self.required_parameters = []
        self.optional_parameters = ["output", "offset", "limit"]
        self.number_of_uris_required = 0

        self.prefix_block = """
PREFIX sem: <http://semanticweb.cs.vu.nl/2009/11/sem/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sem: <http://semanticweb.cs.vu.nl/2009/11/sem/>
                            """
        self.allowed_parameters_block = """
# All allowed parameters:
# output: {output}, offset: {offset}, limit: {limit}, 
# uri.0: {uri_0}, uri.1: {uri_1}
# filter: {filter}, date_filter_block: {date_filter_block}
                                        """

    def _process_input_uris(self, uris):
        if uris is None:
            self.uris = [None, None]
        else:
            # SPARQL queries require URIs wrapped in <,> unless they have
            # PREFIXES
            self.uris = []
            for item in uris:
                if "http" in item:
                    self.uris.append('<' + item + '>')
                else:
                    self.uris.append(item)
            if len(self.uris) == 1:
                self.uris.append(None)
            #self.uris = ['<' + item + '>' for item in uris if "http" in item]

    def _make_date_filter_block(self):
        if self.datefilter != 'None':
            dateparts = self.datefilter.split('-')
            if len(dateparts) >= 1:
                self.date_filter_block = '?d owltime:year "{0}"^^xsd:int . '.format(dateparts[0])
            if len(dateparts) >= 2:
                self.date_filter_block += '?d owltime:month "{0}"^^xsd:int . '.format(dateparts[1])
            if len(dateparts) == 3:
                self.date_filter_block += '?d owltime:day "{0}"^^xsd:int . '.format(dateparts[2])
        else:
            self.date_filter_block = ''
        

    def _check_parameters(self):
        if self.original_uris is None:
            len_uris = 0
        else:
            len_uris =len(self.original_uris)

        if len_uris < self.number_of_uris_required:
            message = "{0} required, {1} supplied".format(
                self.number_of_uris_required, len(self.uris))
            self.error_message.append({"Insufficient_uris_supplied": message})

    def _build_query(self):
        """ Returns a query string. """
        self._check_parameters()

        if len(self.error_message) == 0:
            full_query = (self.prefix_block + 
                          self.allowed_parameters_block + 
                          self.query_template)

            query = full_query.format(offset=self.offset,
                                      limit=self.limit,
                                      output=self.output,
                                      filter=self.filter,
                                      date_filter_block=self.date_filter_block,
                                      uri_0=self.uris[0],
                                      uri_1=self.uris[1])
            return query
        else:
            return None

    def _build_count_query(self):
        """ Returns a count query string. """
        full_query = ("#Counting query\n" + self.prefix_block + 
                          self.allowed_parameters_block + 
                          self.count_template)
        return full_query.format(offset=self.offset,
                                 limit=self.limit,
                                 output=self.output,
                                 filter=self.filter,
                                 date_filter_block=self.date_filter_block,
                                 uri_0=self.uris[0],
                                 uri_1=self.uris[1])

    def submit_query(self,
                     username=os.environ['NEWSREADER_USERNAME'],
                     password=os.environ['NEWSREADER_PASSWORD'],
                     endpoint_url='https://knowledgestore.fbk.eu'
                                  '/nwr/worldcup-hackathon/sparql'):
        """ Submit query to endpoint; return result. """
        payload = {'query': self.query}
        print "\n\n**New query**"
        print self.query
        t0 = time.time()
        try:
            response = request_url(endpoint_url, auth=(username, password),
                                   params=payload,
                                   back_off=False)
        except Exception as e:
            print "Query raised an exception"
            print type(e)
            self.error_message.append({"Query raised an exception:": e})
            t1 = time.time()
            total = t1-t0
        else:
            t1 = time.time()
            total = t1-t0
            print "Time to return from query: {0:.2f} seconds".format(total)
            print "Response code: {0}".format(response.status_code)
            print "From cache: {0}".format(response.from_cache)

            if response and (response.status_code == requests.codes.ok):
                self.json_result = json.loads(response.content)
                self.clean_json = convert_raw_json_to_clean(self.json_result)
            else:
                self.error_message.append({"Response code not OK:": response.status_code})
            #print "From cache: {0}".format(response.from_cache)
        

    def get_total_result_count(self):
        """ Returns result count for query. """
        count_query = CountQuery(self._build_count_query())
        return count_query.get_count()

    def parse_query_results(self):
        # TODO: nicely parsed needs defining; may depend on query
        """ Returns nicely parsed result of query. """
        QueryResult = namedtuple('QueryResult', ' '.join(self.headers))
        # TODO: consider yielding results instead
        results = []
        for result in self.json_result['results']['bindings']:
            values = []
            for header in self.headers:
                values.append(result.get(header, {}).get('value'))
            next_entry = QueryResult._make(values)
            results.append(next_entry)
        return results


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


class types_of_actors(SparqlQuery):

    """ List of types that appear in any event, restricted to dbpedia

    http://127.0.0.1:5000/types_of_actors?output=json&filter=player
    """

    def __init__(self, *args, **kwargs):
        super(types_of_actors, self).__init__(*args, **kwargs)
        self.query_title = 'dbpedia entities that are actors in any event'
        self.query_template = ("""
SELECT ?type (COUNT (*) as ?count) 
WHERE {{
?a rdf:type sem:Actor . 
?a rdf:type ?type . 
FILTER (?type != sem:Actor && 
STRSTARTS(STR(?type), 
"http://dbpedia.org/ontology/") && 
contains(LCASE(str(?type)), "{filter}"))}} 
GROUP BY ?type 
ORDER BY DESC(?count) 
OFFSET {offset} 
LIMIT {limit}
                               """)

        self.count_template = ("""
SELECT (COUNT (distinct ?type) as ?count) 
WHERE {{ 
?a rdf:type sem:Actor . 
?a rdf:type ?type . 
FILTER (?type != sem:Actor && 
STRSTARTS(STR(?type), 
"http://dbpedia.org/ontology/") && 
contains(LCASE(str(?type)), "{filter}"))}}
                                """)

        self.jinja_template = 'table.html'
        self.headers = ['type', 'count']
        self.required_parameters = []
        self.optional_parameters = ["output", "offset", "limit", "filter"]
        self.number_of_uris_required = 0

        self.query = self._build_query()

class event_details_filtered_by_actor(SparqlQuery):

    """ Get event details involving a specified actor (limited to first 100)

        http://127.0.0.1:5000/event_details_filtered_by_actor?uris.0=http://dbpedia.org/resource/David_Beckham&output=json
    """

    def __init__(self, *args, **kwargs):
        super(event_details_filtered_by_actor, self).__init__(*args, **kwargs)
        self.query_title = 'Get event details by actor'
        self.headers = ['event', 'predicate', 'object', 'object_type']
        self.query_template = ("""
SELECT ?event ?predicate ?object 
?object_type 
WHERE {{ 
?event ?predicate ?object . 
OPTIONAL 
{{ 
?object a ?object_type . 
FILTER(STRSTARTS(STR(?object_type), 
"http://semanticweb.cs.vu.nl/2009/11/sem/"))
}} {{ 
SELECT ?event 
WHERE {{ 
?event a sem:Event .
?event sem:hasActor {uri_0} .
}} 
LIMIT {limit} 
OFFSET {offset} 
}} }} 
ORDER BY DESC(?event) 
                               """)

        self.count_template = ("""
SELECT (count(*) as ?count) 
WHERE {{ 
?event ?predicate ?object . 
OPTIONAL 
{{ 
?object a ?object_type . 
FILTER(STRSTARTS(STR(?object_type), 
"http://semanticweb.cs.vu.nl/2009/11/sem/"))
}} {{ 
SELECT ?event 
WHERE {{ 
?event a sem:Event .
?event sem:hasActor {uri_0} .
}} 
LIMIT 100 
OFFSET 0 
}} }}
                               """)

        self.jinja_template = 'table.html'
        self.required_parameters = ["uris"]
        self.optional_parameters = ["output", "offset", "limit"]
        self.number_of_uris_required = 1

        self.query = self._build_query()

class describe_uri(SparqlQuery):

    """ Details of a URI returned by the DESCRIBE query

        http://127.0.0.1:5000/describe_uri?uris.0=http://dbpedia.org/resource/David_Beckham&output=json
    """

    def __init__(self, *args, **kwargs):
        super(describe_uri, self).__init__(*args, **kwargs)
        self.query_title = 'Details of a URI returned by the DESCRIBE query'
        self.query_template = ("""
DESCRIBE {uri_0}
                               """)

        self.count_template = ("")
        self.result_is_tabular = False
        self.jinja_template = 'default.html'

        self.required_parameters = ["uris"]
        self.optional_parameters = ["output", "offset", "limit"]
        self.number_of_uris_required = 1

        self.query = self._build_query()

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
FILTER (contains(LCASE(str(?actor)), "{filter}"))
}}
GROUP BY ?actor ?comment
ORDER BY desc(?count)
OFFSET {offset}
LIMIT {limit}
                               """)

        self.count_template = ("""
SELECT (count(DISTINCT ?actor) as ?count)
WHERE {{ 
?event rdf:type sem:Event . 
?event sem:hasActor ?actor .
?actor rdf:type {uri_0} .
OPTIONAL {{?actor rdfs:comment ?comment .}}
FILTER (contains(LCASE(str(?actor)), "{filter}")) .
}}
                               """)

        self.jinja_template = 'table.html'
        self.headers = ['actor', 'count', 'comment']

        self.required_parameters = ["uris"]
        self.optional_parameters = ["output", "offset", "limit"]
        self.number_of_uris_required = 1

        self.query = self._build_query()

class property_of_actors_of_a_type(SparqlQuery):

    """ Get a property of actors of one type mentioned in the news

    http://127.0.0.1:5000/property_of_actors_of_a_type?uris.0=dbo:SoccerPlayer&uris.1=dbo:height
    """

    def __init__(self, *args, **kwargs):
        super(property_of_actors_of_a_type, self).__init__(*args, **kwargs)
        self.query_title = 'Get a property of actors of a type mentioned in the news'
        self.query_template = ("""
SELECT DISTINCT ?actor ?value where
{{
  ?event a sem:Event . 
  ?event sem:hasActor ?actor .
  ?actor a {uri_0} .
  ?actor {uri_1} ?value . 
}}
order by desc(?value)
LIMIT {limit}
OFFSET {offset}
                               """)

        self.count_template = ("""
SELECT (count (DISTINCT ?actor) as ?count) where
{{
  ?event a sem:Event . 
  ?event sem:hasActor ?actor .
  ?actor a {uri_0} .
  ?actor {uri_1} ?value . 
}}
                               """)

        self.jinja_template = 'table.html'
        self.headers = ['actor', 'value']

        self.required_parameters = ["uris"]
        self.optional_parameters = ["output", "offset", "limit"]
        self.number_of_uris_required = 2

        self.query = self._build_query()

class summary_of_events_with_actor(SparqlQuery):

    """ Get events mentioning a named actor, summarise with count of entries for
        event and date

    http://127.0.0.1:5000/summary_of_events_with_actor?uris.0=dbpedia:David_Beckham
    """

    def __init__(self, *args, **kwargs):
        super(summary_of_events_with_actor, self).__init__(*args, **kwargs)
        self.query_title = 'Get events mentioning a named actor'
        self.query_template = ("""
SELECT 
?event (COUNT (?event) AS ?event_size) ?datetime
WHERE {{
?event ?p ?o .
{{ ?event sem:hasActor {uri_0} .}}
UNION
{{ ?event sem:hasPlace {uri_0} .}}
?event sem:hasTime ?t .
?t owltime:inDateTime ?d .
{date_filter_block}
?t rdfs:label ?datetime .
  FILTER (regex(?datetime,"\\\d{{4}}-\\\d{{2}}"))
}}
GROUP BY ?event ?datetime
ORDER BY ?datetime
OFFSET {offset}
LIMIT {limit}
                               """)

        self.count_template = ("""
SELECT
(COUNT (?event) AS ?count)
WHERE {{
?event ?p ?o .
{{ ?event sem:hasActor {uri_0} .}}
UNION
{{ ?event sem:hasPlace {uri_0} .}}
?event sem:hasTime ?t .
?t owltime:inDateTime ?d .
{date_filter_block}
?t rdfs:label ?datetime .
  FILTER (regex(?datetime,"\\\\d{{4}}-\\\\d{{2}}"))
}}
                               """)

        self.jinja_template = 'table.html'
        self.headers = ['event', 'event_size', 'datetime']

        self.required_parameters = ["uris"]
        self.optional_parameters = ["output", "offset", "limit", "datefilter"]
        self.number_of_uris_required = 1

        self.query = self._build_query()

class actors_sharing_event_with_an_actor(SparqlQuery):

    """ Get actors sharing an event with a named actor with count of occurence

    http://127.0.0.1:5000/actors_sharing_event_with_an_actor?uris.0=dbpedia:David_Beckham
    """

    def __init__(self, *args, **kwargs):
        super(actors_sharing_event_with_an_actor,
              self).__init__(*args, **kwargs)
        self.query_title = 'Get actors sharing an event with a named actor with count of occurence'
        self.query_template = ("""
SELECT DISTINCT ?actor ?actor2 (COUNT(?evt) as ?numEvent) ?comment
WHERE {{
?evt a sem:Event .
?evt sem:hasActor ?actor .
?evt sem:hasActor ?actor2 .
?actor2 a dbo:Person . 
FILTER(?actor = {uri_0} && ?actor2 != ?actor) . 
?actor2 rdfs:comment ?comment .
}}
GROUP BY ?actor2 ?actor ?comment
ORDER BY DESC(?numEvent)
OFFSET {offset}
LIMIT {limit}
                               """)

        self.count_template = ("""
SELECT (COUNT (DISTINCT ?actor2) as ?count)
WHERE {{
?evt a sem:Event .
?evt sem:hasActor ?actor .
?evt sem:hasActor ?actor2 .
?actor2 a dbo:Person . 
FILTER(?actor = {uri_0} && ?actor2 != ?actor) . 
?actor2 rdfs:comment ?comment .
}}
                               """)

        self.jinja_template = 'table.html'
        self.headers = ['actor', 'actor2', 'numEvent', 'comment']

        self.required_parameters = ["uris"]
        self.optional_parameters = ["output", "offset", "limit"]
        self.number_of_uris_required = 1

        self.query = self._build_query()
