#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import SparqlQuery

class property_of_actors_of_a_type(SparqlQuery):

    """ Get a property of actors of one type mentioned in the news

    http://127.0.0.1:5000/property_of_actors_of_a_type?uris.0=dbo:SoccerPlayer&uris.1=dbo:height
    """

    def __init__(self, *args, **kwargs):
        super(property_of_actors_of_a_type, self).__init__(*args, **kwargs)
        self.query_title = 'Get a property of actors of a type mentioned in the news'
        self.url = 'property_of_actors_of_a_type'
        self.example = 'property_of_actors_of_a_type?uris.0=dbo:SoccerPlayer&uris.1=dbo:height'
        self.query_template = ("""
SELECT DISTINCT ?actor ?value where
{{
  ?event a sem:Event . 
  ?event sem:hasActor ?filterfield .
  ?filterfield a {uri_0} .
  {filter_block}
  BIND (?filterfield as ?actor) . 
  ?actor {uri_1} ?value . 
}}
order by desc(?value)
LIMIT {limit}
OFFSET {offset}
                               """)

        self.count_template = ("""
SELECT (count (DISTINCT ?actor) as ?count) where
{{
  ?event a sem:Event . 
  ?event sem:hasActor ?filterfield .
  ?filterfield a {uri_0} .
  {filter_block}
  BIND (?filterfield as ?actor) . 
  ?actor {uri_1} ?value .
}}
                               """)

        self.jinja_template = 'table.html'
        self.headers = ['actor', 'value']

        self.required_parameters = ["uris"]
        self.optional_parameters = ["output", "offset", "limit", "field"]
        self.number_of_uris_required = 2

        self.query = self._build_query()
