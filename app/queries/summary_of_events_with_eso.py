#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import SparqlQuery

class summary_of_events_with_eso(SparqlQuery):

    """ Get events containing a specified eso value
    """

    def __init__(self, *args, **kwargs):
        super(summary_of_events_with_eso, self).__init__(*args, **kwargs)
        self.query_title = 'Get events with a specific eso value'
        self.description = 'eso is an ontology which encompases various semantic framing schemes which give an indication as to the character of an event'
        self.url = 'summary_of_events_with_eso'
        self.world_cup_example = 'summary_of_events_with_eso?uris.0=eso:Renting'
        self.cars_example = 'summary_of_events_with_eso?uris.0=eso:Renting'
        self.query_template = ("""
SELECT ?event (COUNT(*) AS ?event_size) ?datetime ?event_label
WHERE {{
  {{
    SELECT DISTINCT ?event ?datetime ?event_label
    WHERE {{
      ?event a sem:Event .
      ?event rdfs:label ?event_label .
      ?event rdf:type {uri_0} .
      ?event sem:hasTime ?t . 
      ?t owltime:inDateTime ?d .
      {date_filter_block}
      ?t rdfs:label ?datetimetmp .
      FILTER (regex(?datetimetmp,"\\\\d{{4}}-\\\\d{{2}}"))
      BIND (SUBSTR(?datetimetmp,1,10) AS ?datetime)
    }}
    ORDER BY ?datetime
    OFFSET {offset}
    LIMIT {limit}
  }}
  ?event ?p ?o .
}}
GROUP BY ?event ?datetime ?event_label
ORDER BY ?datetime
                               """)

        self.count_template = ("""
SELECT (COUNT(DISTINCT ?event) AS ?count)
WHERE {{
  {{
    SELECT DISTINCT ?event ?datetime
    WHERE {{
      ?event a sem:Event .
      ?event rdfs:label ?event_label .
      ?event rdf:type {uri_0} .
      ?event sem:hasTime ?t . 
      ?t owltime:inDateTime ?d .
      {date_filter_block}
      ?t rdfs:label ?datetimetmp .
      FILTER (regex(?datetimetmp,"\\\\d{{4}}-\\\\d{{2}}"))
      BIND (SUBSTR(?datetimetmp,1,10) AS ?datetime)
    }}
    ORDER BY ?datetime
  }}
  ?event ?p ?o .
}}
                               """)

        self.jinja_template = 'table.html'
        self.headers = ['event', 'datetime', 'event_label', 'event_size']

        self.required_parameters = ["uris"]
        self.optional_parameters = ["output", "offset", "limit", "datefilter"]
        self.number_of_uris_required = 1

        self.query = self._build_query()
