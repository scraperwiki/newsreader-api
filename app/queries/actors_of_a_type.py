#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import SparqlQuery

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
