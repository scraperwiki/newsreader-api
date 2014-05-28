#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import SparqlQuery

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
