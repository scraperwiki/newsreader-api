#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import SparqlQuery

class framenet_frequency_count(SparqlQuery):

    """ Get the frequency of Framenet terms across all events

    """

    def __init__(self, *args, **kwargs):
        super(framenet_frequency_count, self).__init__(*args, **kwargs)
        self.query_title = 'Frequency of Framenet types in events'
        self.description = ("FrameNet provides an indication of the character of"
            " an event, as determined by semantic 'frames'") 
        self.url = 'framenet_frequency_count'
        self.example = 'framenet_frequency_count'
        self.query_template = ("""
SELECT (?filterfield AS ?frame) (COUNT(DISTINCT ?event) AS ?count) ?comment
WHERE {{
  ?event rdf:type ?filterfield  .
  ?g dct:source <http://www.newsreader-project.eu/framenet> .
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
SELECT (COUNT(DISTINCT ?filterfield) AS ?count) ?comment
WHERE {{
  ?event rdf:type ?filterfield  .
  ?g dct:source <http://www.newsreader-project.eu/> .
  GRAPH ?g {{
    ?filterfield a {uri_0} .
    {uri_filter_block}
    OPTIONAL {{ ?filterfield rdfs:comment ?comment }}
  }}
}}
GROUP BY ?filterfield ?comment
                               """)

        self.jinja_template = 'table.html'
        self.headers = ['frame', 'count']

        self.required_parameters = []
        self.optional_parameters = ["output", "offset", "limit", "filter"]
        self.number_of_uris_required = 0

        self.query = self._build_query()
