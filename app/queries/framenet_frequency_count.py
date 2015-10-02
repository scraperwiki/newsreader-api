#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import SparqlQuery

class framenet_frequency_count(SparqlQuery):

    """ Get the frequency of Framenet terms across all events

    """

    def __init__(self, *args, **kwargs):
        super(framenet_frequency_count, self).__init__(*args, **kwargs)
        self.query_title = 'Frequency of Framenet types in events'
        self.description = ("FrameNet provides an indication of the character of"
            " an event, as determined by semantic 'frames'.**This query is very slow"
            " and will timeout the server, contents are available as a file**") 
        self.url = 'framenet_frequency_count'
        self.world_cup_example = 'framenet_frequency_count'
        self.cars_example = 'framenet_frequency_count'
        self.dutchhouse_example = 'framenet_frequency_count'
        self.wikinews_example = 'framenet_frequency_count'
        self.query_template = ("""
SELECT
?frame (count (?frame) AS ?count)
WHERE {{
?event a sem:Event . 
?event a ?filterfield . 
FILTER(STRSTARTS(STR(?filterfield), "http://www.newsreader-project.eu/ontologies/framenet/")) .
BIND (?filterfield AS ?frame) .
}}
GROUP BY ?frame
ORDER by desc(?count)
LIMIT {limit}
OFFSET {offset}
                               """)

        self.count_template = ("""
SELECT
(COUNT (DISTINCT ?frame) AS ?count)
WHERE {{
?event a sem:Event . 
?event a ?filterfield . 
FILTER(STRSTARTS(STR(?filterfield), "http://www.newsreader-project.eu/ontologies/framenet/")) .
BIND (?filterfield AS ?frame) .
}}
                               """)

        self.jinja_template = 'table.html'
        self.headers = ['frame', 'count']

        self.required_parameters = []
        self.optional_parameters = ["output", "filter"]
        self.number_of_uris_required = 0

        self.query = self._build_query()
