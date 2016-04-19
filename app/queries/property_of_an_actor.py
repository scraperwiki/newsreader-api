#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import SparqlQuery

class property_of_an_actor(SparqlQuery):

    """ Get a property of an actor
    """

    def __init__(self, *args, **kwargs):
        super(property_of_an_actor, self).__init__(*args, **kwargs)
        self.query_title = 'Get a property of a particular actor'
        self.description = ('Gives the value of a property for a specified actor')
        self.url = 'property_of_an_actor'
        self.world_cup_example = 'property_of_an_actor/page/1?uris.0=dbpedia:Barack_Obama&uris.1=dbo:birthPlace'
        self.cars_example = 'property_of_an_actor/page/1?uris.0=dbpedia:Barack_Obama&uris.1=dbo:birthPlace'
        self.ft_example = 'property_of_an_actor/page/1?uris.0=dbpedia:Barack_Obama&uris.1=dbo:birthPlace'
        self.wikinews_example = 'property_of_an_actor/page/1?uris.0=dbpedia:Barack_Obama&uris.1=dbo:birthPlace'
        self.query_template = ("""
SELECT ({uri_0} AS ?actor) ?value
WHERE {{
  OPTIONAL {{ {uri_0} {uri_1} ?value }}
}}
ORDER BY DESC(?value)
OFFSET {offset}
LIMIT {limit}
                               """)

        self.count_template = ("""
SELECT (COUNT(*) as ?count){{
SELECT ({uri_0} AS ?actor) ?value
WHERE {{
  OPTIONAL {{ {uri_0} {uri_1} ?value }}
}}
}}
                               """)

        self.jinja_template = 'table.html'
        self.headers = ['actor', 'value']

        self.required_parameters = ["uris"]
        self.optional_parameters = ["output", "offset", "limit", "field"]
        self.number_of_uris_required = 2

        self._make_uri_filter_block()
        self.query = self._build_query()

        def _make_uri_filter_block(self):
            if self.filter != 'none':
                #self.filter_block = 'FILTER (contains(LCASE(str(?filterfield)), "{filter}")) .'.format(filter=self.filter)
                self.uri_filter_block = """?g dct:source <http://dbpedia.org/> . GRAPH ?g {{ ?filterfield rdfs:label ?_label . ?_label bif:contains "{filter}" . }}""".format(filter=self.filter)
            else:
                self.uri_filter_block = ''
