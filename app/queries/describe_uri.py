#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import SparqlQuery

class describe_uri(SparqlQuery):

    """ Details of a URI returned by the DESCRIBE query
    """

    def __init__(self, *args, **kwargs):
        super(describe_uri, self).__init__(*args, **kwargs)
        self.query_title = 'Details of a URI returned by the DESCRIBE query'
        self.description = 'Uses the SPARQL DESCRIBE keyword which returns a network not compatible with HTML display'
        self.url = 'describe_uri'
        self.world_cup_example = 'describe_uri?uris.0=dbpedia:Thierry_Henry&output=json'
        self.cars_example = 'describe_uri?uris.0=dbpedia:Martin_Winterkorn&output=json'
        self.dutchhouse_example = 'describe_uri?uris.0=dbpedia:Martin_Winterkorn&output=json'
        self.query_template = ("""
DESCRIBE {uri_0}
                               """)

        self.count_template = ("")
        self.output = 'json'
        self.result_is_tabular = False
        self.jinja_template = 'default.html'

        self.required_parameters = ["uris"]
        self.optional_parameters = ["output"]
        self.headers = ['**output is a graph**']
        self.number_of_uris_required = 1

        self.query = self._build_query()

    def get_total_result_count(self):
        """ Returns result count for query, exception for this describe query """
        return 0

    def parse_query_results(self):
        # TODO: nicely parsed needs defining; may depend on query
        """ Returns nicely parsed result of query. """
        return self.json_result
