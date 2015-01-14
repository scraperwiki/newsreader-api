#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import SparqlQuery

class summary_of_events_with_two_actors(SparqlQuery):

    """ Get events mentioning a named actor, summarise with count of entries for
        event and date
   """

    def __init__(self, *args, **kwargs):
        super(summary_of_events_with_two_actors, self).__init__(*args, **kwargs)
        self.query_title = 'Get events mentioning two named actors'
        self.description = ('List of events containing two named actors,'
          ' including a link to the article and some summary information')
        self.url = 'summary_of_events_with_two_actors'
        self.example = 'summary_of_events_with_two_actors?uris.0=dbpedia:Alan_Mulally&uris.1=dbpedia:William_Clay_Ford,_Jr.'
        self.query_template = ("""
SELECT ?event (COUNT(*) AS ?event_size) ?datetime ?event_label
WHERE {{
  {{
    SELECT DISTINCT ?event ?datetime ?event_label
    WHERE {{
      ?event sem:hasActor {uri_0} , {uri_1} ;
             sem:hasTime ?t ;
             rdfs:label ?event_label .
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
  ?event ?p ?o
}}
GROUP BY ?event ?datetime ?event_label
ORDER BY ?datetime
                               """)

        self.count_template = ("""
SELECT (COUNT(?event) AS ?count)
WHERE {{
  {{
    SELECT DISTINCT ?event ?datetime ?event_label
    WHERE {{
      ?event sem:hasActor {uri_0} , {uri_1} ;
             sem:hasTime ?t ;
             rdfs:label ?event_label .
      ?t owltime:inDateTime ?d .
      {date_filter_block}
      ?t rdfs:label ?datetimetmp .
      FILTER (regex(?datetimetmp,"\\\\d{{4}}-\\\\d{{2}}"))
      BIND (SUBSTR(?datetimetmp,1,10) AS ?datetime)
    }}
    ORDER BY ?datetime
  }}
  ?event ?p ?o
}}
GROUP BY ?event ?datetime ?event_label
                               """)

        self.jinja_template = 'table.html'
        self.headers = ['event', 'event_size', 'datetime', 'event_label']

        self.required_parameters = ["uris"]
        self.optional_parameters = ["output", "offset", "limit", "datefilter"]
        self.number_of_uris_required = 2

        self.query = self._build_query()
