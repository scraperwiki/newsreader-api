#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import SparqlQuery

class summary_of_events_with_actor_type(SparqlQuery):

    """ Get events mentioning a named actor, summarise with count of entries for
        event and date
    """

    def __init__(self, *args, **kwargs):
        super(summary_of_events_with_actor_type, self).__init__(*args, **kwargs)
        self.query_title = 'Get events mentioning a type of actor'
        self.description = ('A list of events mentioning a specified type of actor'
          ', providing a link to the event and some summary information.')
        self.url = 'summary_of_events_with_actor_type'
        self.world_cup_example = 'summary_of_events_with_actor_type?datefilter=2010-01&uris.0=dbo:GolfPlayer'
        self.cars_example = 'summary_of_events_with_actor_type?datefilter=2010-01&uris.0=dbo:Company'
        self.query_template = ("""
SELECT 
?event (COUNT (?event) AS ?event_size) ?datetime ?actor
WHERE {{
?event ?p ?o .
{{ ?event sem:hasActor ?actor .}}
UNION
{{ ?event sem:hasPlace ?actor .}}
?actor a {uri_0} .
?event sem:hasTime ?t .
?t owltime:inDateTime ?d .
{date_filter_block}
?t rdfs:label ?datetimetmp .
  FILTER (regex(?datetimetmp,"\\\d{{4}}-\\\d{{2}}"))
  BIND (SUBSTR(?datetimetmp,1,10) as ?datetime)
}}
GROUP BY ?event ?datetime ?actor
ORDER BY ?datetime
OFFSET {offset}
LIMIT {limit}
                               """)


        self.count_template = ("""
SELECT 
(COUNT (DISTINCT ?event) AS ?count)
WHERE {{
?event ?p ?o .
{{ ?event sem:hasActor ?actor .}}
UNION
{{ ?event sem:hasPlace ?actor .}}
?actor a {uri_0} .
?event sem:hasTime ?t .
?t owltime:inDateTime ?d .
{date_filter_block}
?t rdfs:label ?datetimetmp .
  FILTER (regex(?datetimetmp,"\\\d{{4}}-\\\d{{2}}"))
  BIND (SUBSTR(?datetimetmp,1,10) as ?datetime)
}}
                               """)

        self.jinja_template = 'table.html'
        self.headers = ['event', 'event_size', 'datetime', 'actor']

        self.required_parameters = ["uris"]
        self.optional_parameters = ["output", "datefilter"]
        self.number_of_uris_required = 1

        self.query = self._build_query()
