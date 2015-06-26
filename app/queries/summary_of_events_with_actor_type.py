#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import SparqlQuery

class summary_of_events_with_actor_type(SparqlQuery):

    """ Get events mentioning a named actor, summarise with count of entries for
        event and date
    """

    def __init__(self, *args, **kwargs):
        super(summary_of_events_with_actor_type, self).__init__(*args, **kwargs)
        self.query_title = 'Get events mentioning a type of actor'
        self.description = ('A list of events mentioning a specified type of actor'
          ', providing a link to the event and some summary information.')
        self.url = 'summary_of_events_with_actor_type'
        self.world_cup_example = 'summary_of_events_with_actor_type?datefilter=2010-01&uris.0=dbo:GolfPlayer'
        self.cars_example = 'summary_of_events_with_actor_type?datefilter=2010-01&uris.0=dbo:Company'
        self.dutchhouse_example = 'summary_of_events_with_actor_type?datefilter=2010-01&uris.0=dbo:Company'

        self.query_template = ("""
SELECT ?event (COUNT (*) AS ?event_size) ?datetime ?actor
WHERE {{
  {{
    SELECT DISTINCT ?event ?datetime ?actor
    WHERE {{
      ?event sem:hasTime ?t .
      ?event sem:hasActor|sem:hasPlace ?actor .
      ?actor a {uri_0} .
      ?t owltime:inDateTime ?d .
      {date_filter_block}
      ?d rdfs:label ?datetime .
    }}
    ORDER BY ?datetime
    OFFSET {offset}
    LIMIT {limit}
  }}
  ?event ?p ?o .
}}
GROUP BY ?event ?datetime ?actor
ORDER BY ?datetime
                               """)

        self.count_template = ("""
SELECT (COUNT(DISTINCT ?event) AS ?count)
WHERE {{
  ?event sem:hasTime ?t .
  ?event sem:hasActor|sem:hasPlace ?actor .
  ?actor a {uri_0} .
  ?t owltime:inDateTime ?d .
  {date_filter_block}
  ?d rdfs:label ?datetime .
}}
                               """)

        self.jinja_template = 'table.html'
        self.headers = ['event', 'event_size', 'datetime', 'actor']

        self.required_parameters = ["uris"]
        self.optional_parameters = ["output", "datefilter"]
        self.number_of_uris_required = 1

        self.query = self._build_query()
