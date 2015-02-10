#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import SparqlQuery

class event_precis(SparqlQuery):

    """ 
    """

    def __init__(self, *args, **kwargs):
        super(event_precis, self).__init__(*args, **kwargs)
        self.query_title = 'Get event precis'
        self.description = 'Get precis for event which is a distillation of the event graph rather than verbatim report.'
        self.url = 'event_precis'
        self.world_cup_example = 'event_precis?uris.0=http://www.newsreader-project.eu/data/cars/2003/06/02/48RT-R260-009F-R155.xml%23ev18'
        self.cars_example = 'event_precis?uris.0=http://www.newsreader-project.eu/data/cars/2003/06/02/48RT-R260-009F-R155.xml%23ev18'
        self.query_template = ("""
SELECT DISTINCT ?subject ?predicate ?object ?graph
WHERE {{
 VALUES ?event {{ {uri_0} }}
 {{
       GRAPH ?graph {{ ?event rdf:type ?object . }}
       BIND (?event as ?subject)
       BIND (rdf:type as ?predicate)
       FILTER (STRSTARTS(STR(?object), "http://www.newsreader-project.eu/domain-ontology"))

 }}
 UNION
 {{
        GRAPH ?graph {{ ?event ?predicate ?object . }}
        BIND (?event as ?subject)
        FILTER (STRSTARTS(STR(?predicate), "http://www.newsreader-project.eu/domain-ontology"))
 }}
 UNION
 {{
        GRAPH ?graph {{ ?event sem:hasActor ?object . }}
        BIND (?event as ?subject)
        BIND (sem:hasActor as ?predicate)
 }}
 UNION
 {{
        GRAPH ?graph {{ ?event sem:hasPlace ?object . }}
        BIND (?event as ?subject)
        BIND (sem:hasPlace as ?predicate)
 }}
 UNION
 {{
        GRAPH ?graph {{ ?event sem:hasTime ?t . }}
        ?t  owltime:inDateTime ?d .
        BIND (?event as ?subject)
        BIND (nwr:cleanedTime as ?predicate)
        BIND (?d as ?object)
 }}
 UNION
 {{
       ?event eso:hasPreSituation ?graph
       GRAPH ?graph {{ ?subject ?predicate ?object . }}
 }}
 UNION
 {{
       ?event eso:hasPostSituation ?graph
       GRAPH ?graph {{ ?subject ?predicate ?object . }}
 }}
 UNION
 {{
       ?event eso:hasDuringSituation ?graph
       GRAPH ?graph {{ ?subject ?predicate ?object . }}
 }}
 UNION
 {{
    {{
    SELECT ?event (COUNT(DISTINCT ?m) AS ?object)
    WHERE {{
      ?event gaf:denotedBy ?mention . 
      BIND (STRBEFORE(STR(?mention), "#") as ?m)
    }}
    GROUP BY ?event
  }}
  BIND (?event AS ?subject)
  BIND ("number of documents" AS ?predicate)
  BIND ("graph" AS ?graph)
 }}
}}""")

        self.count_template = ("""
SELECT (COUNT(*) as ?count)
WHERE{{
SELECT DISTINCT ?subject ?predicate ?object ?graph
WHERE {{
 VALUES ?event {{ {uri_0} }}
 {{
       GRAPH ?graph {{ ?event rdf:type ?object . }}
       BIND (?event as ?subject)
       BIND (rdf:type as ?predicate)
       FILTER (STRSTARTS(STR(?object), "http://www.newsreader-project.eu/domain-ontology"))

 }}
 UNION
 {{
        GRAPH ?graph {{ ?event ?predicate ?object . }}
        BIND (?event as ?subject)
        FILTER (STRSTARTS(STR(?predicate), "http://www.newsreader-project.eu/domain-ontology"))
 }}
 UNION
 {{
        GRAPH ?graph {{ ?event sem:hasActor ?object . }}
        BIND (?event as ?subject)
        BIND (sem:hasActor as ?predicate)
 }}
 UNION
 {{
        GRAPH ?graph {{ ?event sem:hasPlace ?object . }}
        BIND (?event as ?subject)
        BIND (sem:hasPlace as ?predicate)
 }}
 UNION
 {{
        GRAPH ?graph {{ ?event sem:hasTime ?t . }}
        ?t  owltime:inDateTime ?d .
        BIND (?event as ?subject)
        BIND (nwr:cleanedTime as ?predicate)
        BIND (?d as ?object)
 }}
 UNION
 {{
       ?event eso:hasPreSituation ?graph
       GRAPH ?graph {{ ?subject ?predicate ?object . }}
 }}
 UNION
 {{
       ?event eso:hasPostSituation ?graph
       GRAPH ?graph {{ ?subject ?predicate ?object . }}
 }}
 UNION
 {{
       ?event eso:hasDuringSituation ?graph
       GRAPH ?graph {{ ?subject ?predicate ?object . }}
 }}
 UNION
 {{
    {{
    SELECT ?event (COUNT(DISTINCT ?m) AS ?object)
    WHERE {{
      ?event gaf:denotedBy ?mention . 
      BIND (STRBEFORE(STR(?mention), "#") as ?m)
    }}
    GROUP BY ?event
  }}
  BIND (?event AS ?subject)
  BIND ("number of documents" AS ?predicate)
  BIND ("graph" AS ?graph)
 }}
}}
}}""")
        self.jinja_template = 'table.html'
        self.headers = ['subject', 'predicate', 'object', 'graph']

        self.required_parameters = ["uris"]
        self.optional_parameters = ["output"]
        self.number_of_uris_required = 1

        self._make_uri_filter_block()
        self.query = self._build_query()
