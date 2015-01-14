#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import SparqlQuery


class situation_graph(SparqlQuery):

    """ Get situation graph for an event; before, during and after.
    """

    def __init__(self, *args, **kwargs):
        super(situation_graph, self).__init__(*args, **kwargs)
        self.query_title = 'Get situation graph'
        self.description = 'Gets the situation graph for an event which tells us about changes of state during that event'
        self.url = 'situation_graph'
        self.world_cup_example = 'situation_graph?uris.0=http://www.newsreader-project.eu/data/cars/2003/06/02/48RT-R260-009F-R155.xml%23ev18'
        self.cars_example = 'situation_graph?uris.0=http://www.newsreader-project.eu/data/cars/2003/06/02/48RT-R260-009F-R155.xml%23ev18'
        self.query_template = ("""
SELECT ?timeline ?subject ?predicate ?object
WHERE {{
 VALUES ?event {{ {uri_0} }}
 ?event rdf:type sem:Event .
 {{
       ?event eso:hasPreSituation ?g
       GRAPH ?g {{ ?subject ?predicate ?object . }}
       BIND ("before" as ?timeline)
 }}
 UNION
 {{
       ?event eso:hasDuringSituation ?g
       GRAPH ?g {{ ?subject ?predicate ?object . }}
       BIND ("during" as ?timeline)
 }}
 UNION
 {{
       ?event eso:hasPostSituation ?g
       GRAPH ?g {{ ?subject ?predicate ?object . }}
       BIND ("after" as ?timeline)
 }}
}}
                """)

        self.count_template = ("""
SELECT (COUNT (?timeline) AS ?count)
WHERE {{
 VALUES ?event {{ {uri_0} }}
 ?event rdf:type sem:Event .
 {{
       ?event eso:hasPreSituation ?g
       GRAPH ?g {{ ?subject ?predicate ?object . }}
       BIND ("before" as ?timeline)
 }}
 UNION
 {{
       ?event eso:hasDuringSituation ?g
       GRAPH ?g {{ ?subject ?predicate ?object . }}
       BIND ("during" as ?timeline)
 }}
 UNION
 {{
       ?event eso:hasPostSituation ?g
       GRAPH ?g {{ ?subject ?predicate ?object . }}
       BIND ("after" as ?timeline)
 }}
}}
                """)

        self.jinja_template = 'table.html'
        self.headers = ['timeline', 'subject', 'predicate', 'object']

        self.required_parameters = ["uris"]
        self.optional_parameters = ["output", "offset", "limit"]
        self.number_of_uris_required = 1

        self._make_uri_filter_block()
        self.query = self._build_query()
