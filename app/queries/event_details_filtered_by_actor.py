#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import SparqlQuery

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
