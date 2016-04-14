#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import SparqlQuery

class properties_of_a_type(SparqlQuery):
    """ Get the properties defined for a type
    """

    def __init__(self, *args, **kwargs):
        super(properties_of_a_type,
              self).__init__(*args, **kwargs)
        self.query_title = 'Get the properties of a type'
        self.description = ('Lists all the available properties of a type of '
            'actor, e.g. dbo:SoccerPlayer have properties like height, birthdays,'
            'positions, teams, nationality and so forth. The type_count is the number of such actors'
            ', the value_count is the number of instances of the property')
        self.url = 'properties_of_a_type'
        self.world_cup_example = 'properties_of_a_type?uris.0=dbo:Stadium'
        self.cars_example = 'properties_of_a_type?uris.0=dbo:Company'
        self.ft_example = 'properties_of_a_type?uris.0=dbo:Company'
        self.query_template = ("""
SELECT ?property (COUNT(DISTINCT ?pl) AS ?type_count) (COUNT(DISTINCT ?o) AS ?value_count)
WHERE {{
  ?pl a {uri_0} .
  ?pl ?property ?o .
}}
GROUP BY ?property
ORDER BY DESC(?type_count)
LIMIT {limit}
OFFSET {offset}
                               """)

        self.count_template = ("""
SELECT (COUNT(DISTINCT ?property) AS ?count) 
WHERE {{
  ?pl a {uri_0} .
  ?pl ?property ?o .
}}
                               """)

        self.jinja_template = 'table.html'
        self.headers = ['property', 'type_count', 'value_count']

        self.required_parameters = ["uris"]
        self.optional_parameters = ["output", "offset", "limit"]
        self.number_of_uris_required = 1

        self.query = self._build_query()
