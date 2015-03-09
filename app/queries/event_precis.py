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
  {{
    {uri_0} eso:hasPreSituation|eso:hasPostSituation|eso:hasDuringSituation ?graph .
    GRAPH ?graph {{ ?subject ?predicate  ?object }}
  }} UNION {{
    BIND ({uri_0} as ?subject)
    {{
      GRAPH ?graph {{ {uri_0} ?predicate ?object }}
      FILTER (?predicate = sem:hasActor ||
              ?predicate = sem:hasPlace ||
              ?predicate = rdf:type && EXISTS {{ ?object rdfs:isDefinedBy eso: }} ||
              EXISTS {{ ?predicate rdfs:isDefinedBy eso: }} )
    }} UNION {{
      GRAPH ?graph {{ {uri_0} sem:hasTime ?t }}
      ?t owltime:inDateTime ?object .
      BIND (nwr:cleanedTime as ?predicate)
    }} UNION {{
      SELECT ("number of documents" AS ?predicate) ("graph" AS ?graph)
             (COUNT(DISTINCT STRBEFORE(STR(?m), "#")) AS ?object)
      WHERE {{ {uri_0} gaf:denotedBy ?m }}
    }}
  }}
}}
                               """)

        self.count_template = ("""
SELECT (COUNT(*) as ?count)
WHERE{{
SELECT DISTINCT ?subject ?predicate ?object ?graph
WHERE {{
  {{
    {uri_0} eso:hasPreSituation|eso:hasPostSituation|eso:hasDuringSituation ?graph .
    GRAPH ?graph {{ ?subject ?predicate  ?object }}
  }} UNION {{
    BIND ({uri_0} as ?subject)
    {{
      GRAPH ?graph {{ {uri_0} ?predicate ?object }}
      FILTER (?predicate = sem:hasActor ||
              ?predicate = sem:hasPlace ||
              ?predicate = rdf:type && EXISTS { ?object rdfs:isDefinedBy eso: } ||
              EXISTS {{ ?predicate rdfs:isDefinedBy eso: }} )
    }} UNION {{
      GRAPH ?graph {{ {uri_0} sem:hasTime ?t }}
      ?t owltime:inDateTime ?object .
      BIND (nwr:cleanedTime as ?predicate)
    }} UNION {{
      SELECT ("number of documents" AS ?predicate) ("graph" AS ?graph)
             (COUNT(DISTINCT STRBEFORE(STR(?m), "#")) AS ?object)
      WHERE {{ {uri_0} gaf:denotedBy ?m }}
    }}
  }}
}}
}}
                               """)

        self.jinja_template = 'table.html'
        self.headers = ['subject', 'predicate', 'object', 'graph']

        self.required_parameters = ["uris"]
        self.optional_parameters = ["output"]
        self.number_of_uris_required = 1

        self._make_uri_filter_block()
        self.query = self._build_query()
