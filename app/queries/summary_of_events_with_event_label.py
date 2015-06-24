#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import SparqlQuery

class summary_of_events_with_event_label(SparqlQuery):

    """ Get events with labels containing a specified string
    """

    def __init__(self, *args, **kwargs):
        super(summary_of_events_with_event_label, self).__init__(*args, **kwargs)
        self.query_title = 'Search for events with a specified label'
        self.description = 'The event label gives an indication as to the character of an event'
        self.url = 'summary_of_events_with_event_label'
        self.world_cup_example = 'summary_of_events_with_event_label?filter=bribe&datefilter=2010'
        self.cars_example = 'summary_of_events_with_event_label?filter=bribe&datefilter=2010'
        self.dutchhouse_example = 'summary_of_events_with_event_label?filter=bribe&datefilter=2010'
        self.query_template = ("""
SELECT ?event (COUNT(*) AS ?event_size) ?datetime ?event_label
WHERE {{
  {{
    SELECT DISTINCT ?event ?datetime (?filterfield AS ?event_label)
    WHERE {{
      ?event sem:hasTime ?t ; rdfs:label ?filterfield .
      {filter_block}
      ?t owltime:inDateTime ?d .
      {date_filter_block}
      ?d rdfs:label ?datetime .
    }}
    ORDER BY ?datetime
    OFFSET {offset}
    LIMIT {limit}
  }}
  ?event ?p ?o
}}
GROUP BY ?event ?datetime ?event_label
ORDER BY ?datetime
                               """)

        self.count_template = ("""
SELECT (COUNT(DISTINCT ?event) AS ?count)
WHERE {{
  ?event sem:hasTime ?t ; rdfs:label ?filterfield .
  {filter_block}
  ?t owltime:inDateTime ?d .
  {date_filter_block}
  ?d rdfs:label ?datetime .
}}
                               """)

        self.jinja_template = 'table.html'
        self.headers = ['event', 'datetime', 'event_label','event_size']

        self.required_parameters = ["filter"]
        self.optional_parameters = ["output", "datefilter"]
        self.number_of_uris_required = 0

        self.query = self._build_query()
