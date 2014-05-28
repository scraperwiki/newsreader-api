#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import SparqlQuery

class actors_sharing_event_with_an_actor(SparqlQuery):

    """ Get actors sharing an event with a named actor with count of occurence

    http://127.0.0.1:5000/actors_sharing_event_with_an_actor?uris.0=dbpedia:David_Beckham
    """

    def __init__(self, *args, **kwargs):
        super(actors_sharing_event_with_an_actor,
              self).__init__(*args, **kwargs)
        self.query_title = 'Get actors sharing an event with a named actor with count of occurence'
        self.query_template = ("""
SELECT DISTINCT ?actor ?actor2 (COUNT(?evt) as ?numEvent) ?comment
WHERE {{
?evt a sem:Event .
?evt sem:hasActor ?actor .
?evt sem:hasActor ?actor2 .
?actor2 a dbo:Person . 
FILTER(?actor = {uri_0} && ?actor2 != ?actor) . 
?actor2 rdfs:comment ?comment .
}}
GROUP BY ?actor2 ?actor ?comment
ORDER BY DESC(?numEvent)
OFFSET {offset}
LIMIT {limit}
                               """)

        self.count_template = ("""
SELECT (COUNT (DISTINCT ?actor2) as ?count)
WHERE {{
?evt a sem:Event .
?evt sem:hasActor ?actor .
?evt sem:hasActor ?actor2 .
?actor2 a dbo:Person . 
FILTER(?actor = {uri_0} && ?actor2 != ?actor) . 
?actor2 rdfs:comment ?comment .
}}
                               """)

        self.jinja_template = 'table.html'
        self.headers = ['actor', 'actor2', 'numEvent', 'comment']

        self.required_parameters = ["uris"]
        self.optional_parameters = ["output", "offset", "limit"]
        self.number_of_uris_required = 1

        self.query = self._build_query()
