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
        self.dsecription = ('The types of actors, i.e. dbo:SoccerPlayer found' 
            ' in any event')
        self.url = 'types_of_actors'
        self.example = 'types_of_actors?filter=player'
        self.query_template = ("""
SELECT ?type (COUNT(DISTINCT ?a) AS ?count)
WHERE {{
  {{
    SELECT DISTINCT (?filterfield AS ?type)
    WHERE {{
      ?g dct:source <http://dbpedia.org/> .
      GRAPH ?g {{
        ?filterfield a owl:Class .
        FILTER (?filterfield != sem:Actor)
        FILTER (STRSTARTS(STR(?filterfield),
                "http://dbpedia.org/ontology/"))
        {uri_filter_block}
      }}
    }}
  }}
  ?a a sem:Actor , ?type .
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
      GRAPH ?g {{
        ?filterfield a owl:Class .
        FILTER (?filterfield != sem:Actor)
        FILTER (STRSTARTS(STR(?filterfield),
                "http://dbpedia.org/ontology/"))
        {uri_filter_block}
      }}
    }}
  }}
  ?a a sem:Actor , ?type .
}}
GROUP BY ?type
                                """)

        self.jinja_template = 'table.html'
        self.headers = ['type', 'count']
        self.required_parameters = []
        self.optional_parameters = ["output", "offset", "limit", "filter"]
        self.number_of_uris_required = 0

        self.query = self._build_query()
