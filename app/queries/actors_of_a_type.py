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
        self.query_title = 'Actors of a specified type'
        self.description = 'Get actors of a specified type, i.e dbo:people with the option to filter the URI with a text string i.e. "David"'
        self.url = 'actors_of_a_type'
        self.example = 'actors_of_a_type?uris.0=dbo:Person&filter=david'
        self.query_template = ("""
SELECT (?filterfield AS ?actor) (COUNT(DISTINCT ?event) AS ?count) ?comment
WHERE {{
  ?event sem:hasActor ?filterfield  .
  ?g dct:source <http://dbpedia.org/> .
  GRAPH ?g {{
    ?filterfield a {uri_0} .
    {uri_filter_block}
    OPTIONAL {{ ?filterfield rdfs:comment ?comment }}
  }}
}}
GROUP BY ?filterfield ?comment
ORDER BY desc(?count)
OFFSET {offset}
LIMIT {limit}
                               """)

        self.count_template = ("""
SELECT (COUNT(DISTINCT ?filterfield) AS ?count)
WHERE {{
  ?event sem:hasActor ?filterfield  .
  ?g dct:source <http://dbpedia.org/> .
  GRAPH ?g {{
    ?filterfield a {uri_0} .
    {uri_filter_block}
    OPTIONAL {{ ?filterfield rdfs:comment ?comment }}
  }}
}}
                               """)

        self.jinja_template = 'table.html'
        self.headers = ['actor', 'count', 'comment']

        self.required_parameters = ["uris"]
        self.optional_parameters = ["output", "offset", "limit"]
        self.number_of_uris_required = 1

        self._make_uri_filter_block()
        self.query = self._build_query()
