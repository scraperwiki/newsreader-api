#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import SparqlQuery

class summary_of_events_with_actor(SparqlQuery):

    """ Get events mentioning a named actor, summarise with count of entries for
        event and date

    http://127.0.0.1:5000/summary_of_events_with_actor?uris.0=dbpedia:David_Beckham
    """

    def __init__(self, *args, **kwargs):
        super(summary_of_events_with_actor, self).__init__(*args, **kwargs)
        self.query_title = 'Get events mentioning a named actor'
        self.description = ('A list of events mentioning a specified actor'
          ', providing a link to the event and some summary information.')
        self.url = 'summary_of_events_with_actor'
        self.example = 'summary_of_events_with_actor?uris.0=dbpedia:David_Beckham'
        self.query_template = ("""
SELECT ?event (COUNT(*) AS ?event_size) ?datetime ?event_label
WHERE {{
  {{
    SELECT DISTINCT ?event ?datetime ?event_label
    WHERE {{
      {{ ?event sem:hasActor {uri_0} }} UNION {{ ?event sem:hasPlace {uri_0} }}
      ?event sem:hasTime ?t ; rdfs:label ?event_label .
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
SELECT (COUNT(DISTINCT ?event) as ?count)
WHERE {{
  {{
    SELECT DISTINCT ?event ?datetime
    WHERE {{
      {{ ?event sem:hasActor {uri_0} }} UNION {{ ?event sem:hasPlace {uri_0} }}
      ?event sem:hasTime ?t ; rdfs:label ?event_label .
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
        self.headers = ['event', 'event_size', 'datetime']

        self.required_parameters = ["uris"]
        self.optional_parameters = ["output", "offset", "limit", "datefilter"]
        self.number_of_uris_required = 1

        self.query = self._build_query()
