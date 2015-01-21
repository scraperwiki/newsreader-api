#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import SparqlQuery

class actors_of_a_type(SparqlQuery):

    """ Get actors, counts and comments for actors with a specified type
    """

    def __init__(self, *args, **kwargs):
        super(actors_of_a_type, self).__init__(*args, **kwargs)
        self.query_title = 'Actors of a specified type'
        self.description = 'Get actors of a specified type, i.e dbo:people with the option to filter the type comment with a text string i.e. "David"'
        self.url = 'actors_of_a_type'
        self.world_cup_example = 'actors_of_a_type?uris.0=dbo:Person&filter=david'
        self.cars_example = 'actors_of_a_type?uris.0=dbo:Company&filter=motor'
        self.query_template = ("""
SELECT (?filterfield AS ?actor) (COUNT(DISTINCT ?event) AS ?count) ?comment
WHERE {{
  ?event sem:hasActor ?filterfield  .
  ?g1 dct:source <http://dbpedia.org/> .
  GRAPH ?g1 {{
    ?filterfield a {uri_0} .
  }}
  {uri_filter_block}
  OPTIONAL {{ ?filterfield rdfs:comment ?comment }}
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
  ?g1 dct:source <http://dbpedia.org/> .
  GRAPH ?g1 {{
    ?filterfield a {uri_0} .
  }}
  {uri_filter_block}
  OPTIONAL {{ ?filterfield rdfs:comment ?comment }}
}}
                               """)

        self.jinja_template = 'table.html'
        self.headers = ['actor', 'count', 'comment']

        self.required_parameters = ["uris"]
        self.optional_parameters = ["output", "offset", "limit"]
        self.number_of_uris_required = 1

        self._make_uri_filter_block()
        self.query = self._build_query()

    def _make_uri_filter_block(self):
            if self.filter != 'none':
                #self.filter_block = 'FILTER (contains(LCASE(str(?filterfield)), "{filter}")) .'.format(filter=self.filter)
                self.uri_filter_block = """?g2 dct:source <http://dbpedia.org/> .
                                           GRAPH ?g2 
                    {{ ?filterfield rdfs:label ?_label . ?_label bif:contains "{filter}" . }}""".format(filter=self.filter)
            else:
                self.uri_filter_block = ''
