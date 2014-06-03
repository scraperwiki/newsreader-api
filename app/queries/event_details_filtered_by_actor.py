#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import SparqlQuery

class event_details_filtered_by_actor(SparqlQuery):

    """ Get event details involving a specified actor (limited to first 100)

        http://127.0.0.1:5000/event_details_filtered_by_actor?uris.0=http://dbpedia.org/resource/David_Beckham&output=json
    """

    def __init__(self, *args, **kwargs):
        super(event_details_filtered_by_actor, self).__init__(*args, **kwargs)
        self.query_title = 'Event details for events involving a specified actor'
        self.description = ('Event details for events involving a specified actor,'
                           ' i.e. a list of events involving dbpedia:David_Beckham.'
                           ' The number of entries describing an event varies, so the result count is not very meaningful.')
        self.url = 'event_details_filtered_by_actor'
        self.example = 'event_details_filtered_by_actor?uris.0=dbpedia:David_Beckham'
        self.headers = ['event', 'property', 'value']
        self.query_template = ("""
SELECT ?event ?property ?value  
WHERE {{ 
?event ?property ?value . 
{{ 
SELECT ?event 
WHERE {{ 
?event a sem:Event .
?event sem:hasActor {uri_0} .
}} 
LIMIT {limit} 
OFFSET {offset} 
}} }} 
ORDER BY DESC(?event) 
                               """)

        self.count_template = ("""
SELECT (count(*) as ?count) 
WHERE {{ 
?event ?property ?value . 
{{ 
SELECT ?event 
WHERE {{ 
?event a sem:Event .
?event sem:hasActor {uri_0} .
}} 
LIMIT 100 
OFFSET 0 
}} }}
                               """)

        self.jinja_template = 'table.html'
        self.required_parameters = ["uris"]
        self.optional_parameters = ["output", "offset", "limit"]
        self.number_of_uris_required = 1

        self.query = self._build_query()
