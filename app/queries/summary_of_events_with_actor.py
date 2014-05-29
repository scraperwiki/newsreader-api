#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import SparqlQuery

class summary_of_events_with_actor(SparqlQuery):

    """ Get events mentioning a named actor, summarise with count of entries for
        event and date

    http://127.0.0.1:5000/summary_of_events_with_actor?uris.0=dbpedia:David_Beckham
    """

    def __init__(self, *args, **kwargs):
        super(summary_of_events_with_actor, self).__init__(*args, **kwargs)
        self.query_title = 'Get events mentioning a named actor'
        self.query_template = ("""
SELECT 
?event (COUNT (?event) AS ?event_size) ?datetime
WHERE {{
?event ?p ?o .
{{ ?event sem:hasActor {uri_0} .}}
UNION
{{ ?event sem:hasPlace {uri_0} .}}
?event sem:hasTime ?t .
?t owltime:inDateTime ?d .
{date_filter_block}
?t rdfs:label ?datetime .
  FILTER (regex(?datetime,"\\\d{{4}}-\\\d{{2}}"))
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
{{ ?event sem:hasActor {uri_0} .}}
UNION
{{ ?event sem:hasPlace {uri_0} .}}
?event sem:hasTime ?t .
?t owltime:inDateTime ?d .
{date_filter_block}
?t rdfs:label ?datetime .
  FILTER (regex(?datetime,"\\\\d{{4}}-\\\\d{{2}}"))
}}
}}
                               """)

        self.jinja_template = 'table.html'
        self.headers = ['event', 'event_size', 'datetime']

        self.required_parameters = ["uris"]
        self.optional_parameters = ["output", "offset", "limit", "datefilter"]
        self.number_of_uris_required = 1

        self.query = self._build_query()
