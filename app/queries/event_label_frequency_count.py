#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import SparqlQuery

class event_label_frequency_count(SparqlQuery):

    """ Get the frequency of event labels across all events
    """

    def __init__(self, *args, **kwargs):
        super(event_label_frequency_count, self).__init__(*args, **kwargs)
        self.query_title = 'Frequency of event labels in events'
        self.description = ("The event label provides an indication of the character of"
            " an event") 
        self.url = 'event_label_frequency_count'
        self.world_cup_example = 'event_label_frequency_count?filter=bribe+OR+bribery'
        self.cars_example = 'event_label_frequency_count?filter=takeover+OR+buyout'
        self.query_template = ("""
SELECT
(?filterfield AS ?event_label) (COUNT(DISTINCT ?event) AS ?count)
WHERE {{
?event a sem:Event .
?event rdfs:label ?filterfield . 
{filter_block}
}}
GROUP BY ?filterfield
ORDER by desc(?count)
OFFSET {offset}
LIMIT {limit}
                               """)

        self.count_template = ("""
SELECT
(COUNT (DISTINCT ?filterfield) AS ?count)
WHERE {{
?event a sem:Event .
?event rdfs:label ?filterfield . 
{filter_block}
}}
                               """)

        self.jinja_template = 'table.html'
        self.headers = ['event_label', 'count']

        self.required_parameters = []
        self.optional_parameters = ["output", "offset", "limit", "filter"]
        self.number_of_uris_required = 0

        self.query = self._build_query()
