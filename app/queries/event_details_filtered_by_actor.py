#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import SparqlQuery

class event_details_filtered_by_actor(SparqlQuery):

    """ Get event details involving a specified actor (limited to first 100)
    """

    def __init__(self, *args, **kwargs):
        super(event_details_filtered_by_actor, self).__init__(*args, **kwargs)
        self.query_title = 'Event details for events involving a specified actor'
        self.description = ('Event details for events involving a specified actor,'
                           ' i.e. a list of events involving dbpedia:David_Beckham.'
                           ' The number of entries describing an event varies, so the result count is not very meaningful.')
        self.url = 'event_details_filtered_by_actor'
        self.world_cup_example = 'event_details_filtered_by_actor?uris.0=dbpedia:David_Beckham'
        self.cars_example = 'event_details_filtered_by_actor?uris.0=dbpedia:Martin_Winterkorn'
        self.headers = ['event', 'predicate', 'object', "object_type"]
        self.query_template = ("""
SELECT ?event ?predicate ?object (SAMPLE(?type) AS ?object_type)
WHERE {{
  {{
    SELECT DISTINCT ?event
    WHERE {{
      ?event sem:hasActor {uri_0} .
    }}
    ORDER BY DESC(?event)
    OFFSET {offset}
    LIMIT {limit}
  }}
  ?event ?predicate ?object .
  OPTIONAL {{
    ?object a ?type .
    FILTER ( ?type = sem:Actor || ?type = sem:Place ||
             ?type = sem:Time  || ?type = sem:Event )
  }}
}}
GROUP BY ?event ?predicate ?object
ORDER BY DESC(?event) ?predicate ?object 
                               """)

        self.count_template = ("""
SELECT (COUNT(DISTINCT ?event) AS ?count)
    WHERE {{
      ?event sem:hasActor {uri_0} .
    }}
                               """)

        self.jinja_template = 'table.html'
        self.required_parameters = ["uris"]
        self.optional_parameters = ["output", "offset", "limit"]
        self.number_of_uris_required = 1

        self.query = self._build_query()
