#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import SparqlQuery

class properties_of_a_type(SparqlQuery):
    """ Get the properties defined for a type

    http://127.0.0.1:5000/properties_of_a_type?uris.0=dbo:SoccerPlayer
    """

    def __init__(self, *args, **kwargs):
        super(properties_of_a_type,
              self).__init__(*args, **kwargs)
        self.query_title = 'Get the properties of a type'
        self.query_template = ("""
SELECT DISTINCT ?property
WHERE {
?pl ?property ?o .
?pl a {uri_0} .
}
LIMIT {limit}
OFFSET {offset}
                               """)

        self.count_template = ("""
SELECT (COUNT (DISTINCT ?property) as ?count)
WHERE {
?pl ?property ?o .
?pl a {uri_0} .
}
                               """)

        self.jinja_template = 'table.html'
        self.headers = ['property']

        self.required_parameters = ["uris"]
        self.optional_parameters = ["output", "offset", "limit"]
        self.number_of_uris_required = 1

        self.query = self._build_query()
