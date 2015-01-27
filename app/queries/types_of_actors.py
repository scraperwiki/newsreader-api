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
        self.query_title = 'Types of actors'
        self.description = ('The types of actors, e.g. dbo:RacingDriver found' 
            ' in any event. The unfiltered list is precomputable.')
        self.url = 'types_of_actors'
        self.world_cup_example = 'types_of_actors?filter=player'
        self.cars_example = 'types_of_actors?filter=driver'
        self.query_template = ("""
SELECT ?type (COUNT(DISTINCT ?a) AS ?count)
WHERE {{
  {{
    SELECT DISTINCT (?filterfield AS ?type)
    WHERE {{
      ?g dct:source <http://dbpedia.org/> .
       ?filterfield a owl:Class .
        FILTER (?filterfield != sem:Actor)
        FILTER (STRSTARTS(STR(?filterfield),
                "http://dbpedia.org/ontology/"))
      GRAPH ?g {{
        {uri_filter_block}
      }}
    }}
  }}
  ?a a ?type .
  ?e sem:hasActor ?a .
}}
GROUP BY ?type
ORDER BY DESC(?count)
OFFSET {offset}
LIMIT {limit}
                               """)

        self.count_template = ("""
SELECT (COUNT(DISTINCT ?type) AS ?count)
WHERE {{
  {{
    SELECT DISTINCT (?filterfield AS ?type)
    WHERE {{
      ?g dct:source <http://dbpedia.org/> .
      ?filterfield a owl:Class .
        FILTER (?filterfield != sem:Actor)
        FILTER (STRSTARTS(STR(?filterfield),
                "http://dbpedia.org/ontology/"))
      GRAPH ?g {{
        {uri_filter_block}
      }}
    }}
  }}
  ?a a ?type .
  ?e sem:hasActor ?a .
}}
                                """)

        self.jinja_template = 'table.html'
        self.headers = ['type', 'count']
        self.required_parameters = []
        self.optional_parameters = ["output", "offset", "limit", "filter"]
        self.number_of_uris_required = 0

        self.query = self._build_query()
