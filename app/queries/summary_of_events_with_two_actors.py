#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import SparqlQuery

class summary_of_events_with_two_actors(SparqlQuery):

    """ Get events mentioning a named actor, summarise with count of entries for
        event and date

    http://127.0.0.1:5000/summary_of_events_with_two_actors?uris.0=dbpedia:David_Beckham&uris.1=dbpedia:Sepp_Blatter
    """

    def __init__(self, *args, **kwargs):
        super(summary_of_events_with_two_actors, self).__init__(*args, **kwargs)
        self.query_title = 'Get events mentioning two named actors'
        self.url = 'summary_of_events_with_two_actors'
        self.example = 'summary_of_events_with_two_actors?uris.0=dbpedia:David_Beckham&uris.1=dbpedia:Sepp_Blatter'
        self.query_template = ("""
SELECT 
?event (COUNT (?event) AS ?event_size) ?datetime
WHERE {{
?event ?p ?o .
{{ 
?event sem:hasActor {uri_0} .
?event sem:hasActor {uri_1} .
}}
?event sem:hasTime ?t .
?t owltime:inDateTime ?d .
{date_filter_block}
?t rdfs:label ?datetimetmp .
  FILTER (regex(?datetimetmp,"\\\d{{4}}-\\\d{{2}}"))
  BIND (SUBSTR(?datetimetmp,1,10) as ?datetime)
}}
GROUP BY ?event ?datetime
ORDER BY ?datetime
OFFSET {offset}
LIMIT {limit}
                               """)

        self.count_template = ("""
SELECT (COUNT(*) as ?count) {{
SELECT
DISTINCT ?event ?datetime
WHERE {{
?event ?p ?o .
{{ 
?event sem:hasActor {uri_0} .
?event sem:hasActor {uri_1} .
}}
UNION
{{ ?event sem:hasPlace {uri_0} .}}
?event sem:hasTime ?t .
?t owltime:inDateTime ?d .
{date_filter_block}
?t rdfs:label ?datetimetmp .
  FILTER (regex(?datetimetmp,"\\\\d{{4}}-\\\\d{{2}}"))
  BIND (SUBSTR(?datetimetmp,1,10) as ?datetime)
}}
}}
                               """)

        self.jinja_template = 'table.html'
        self.headers = ['event', 'event_size', 'datetime']

        self.required_parameters = ["uris"]
        self.optional_parameters = ["output", "offset", "limit", "datefilter"]
        self.number_of_uris_required = 2

        self.query = self._build_query()
