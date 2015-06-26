#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import SparqlQuery

class summary_of_events_with_actor(SparqlQuery):

    """ Get events mentioning a named actor, summarise with count of entries for
        event and date
    """

    def __init__(self, *args, **kwargs):
        super(summary_of_events_with_actor, self).__init__(*args, **kwargs)
        self.query_title = 'Get events mentioning a named actor'
        self.description = ('A list of events mentioning a specified actor'
          ', providing a link to the event and some summary information.')
        self.url = 'summary_of_events_with_actor'
        self.world_cup_example = 'summary_of_events_with_actor?uris.0=dbpedia:Thierry_Henry'
        self.cars_example = 'summary_of_events_with_actor?uris.0=dbpedia:Alan_Mulally'
        self.dutchhouse_example = 'summary_of_events_with_actor?uris.0=dbpedianl:Rijkman_Groenink'
        self.query_template = ("""
SELECT ?event (COUNT(*) AS ?event_size) ?datetime ?event_label
WHERE {{
  {{
    SELECT DISTINCT ?event ?datetime ?event_label
    WHERE {{
      ?event sem:hasActor|sem:hasPlace {uri_0} .
      ?event rdfs:label ?event_label ; sem:hasTime ?t .
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
GROUP BY ?event ?datetime ?event_label
ORDER BY ?datetime
                               """)

        self.count_template = ("""
SELECT (COUNT(DISTINCT ?event) as ?count)
WHERE {{
  ?event sem:hasActor|sem:hasPlace {uri_0} .
  ?event rdfs:label ?event_label ; sem:hasTime ?t .
  ?t owltime:inDateTime ?d .
  {date_filter_block}
  ?d rdfs:label ?datetime .
}}
                               """)

        self.jinja_template = 'table.html'
        self.headers = ['event', 'event_size', 'datetime', 'event_label']

        self.required_parameters = ["uris"]
        self.optional_parameters = ["output", "datefilter"]
        self.number_of_uris_required = 1

        self.query = self._build_query()
