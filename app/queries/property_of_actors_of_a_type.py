#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import SparqlQuery

class property_of_actors_of_a_type(SparqlQuery):

    """ Get a property of actors of one type mentioned in the news
    """

    def __init__(self, *args, **kwargs):
        super(property_of_actors_of_a_type, self).__init__(*args, **kwargs)
        self.query_title = 'Get a property of actors of a type mentioned in the news'
        self.description = ('Lists the values of a named property of a type,'
          'such as the height of dbo:SoccerPlayer.')
        self.url = 'property_of_actors_of_a_type'
        self.world_cup_example = 'property_of_actors_of_a_type/page/1?uris.1=dbo:height&filter=david&uris.0=dbo:SoccerPlayer'
        self.cars_example = 'property_of_actors_of_a_type?uris.1=dbo:foundedBy&filter=motor&uris.0=dbo:Company'
        self.query_template = ("""
SELECT DISTINCT (?filterfield AS ?actor) ?value
WHERE {{
  ?event sem:hasActor ?filterfield .
  ?filterfield a {uri_0} ; {uri_1} ?value .
    {uri_filter_block}
}}
ORDER BY DESC(?value)
OFFSET {offset}
LIMIT {limit}
                               """)

        self.count_template = ("""
SELECT (COUNT(*) as ?count){{
SELECT DISTINCT (?filterfield AS ?actor) ?value
WHERE {{
  ?event sem:hasActor ?filterfield .
  ?filterfield a {uri_0} ; {uri_1} ?value .
    {uri_filter_block}
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
