#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import SparqlQuery

class eso_frequency_count(SparqlQuery):

    """ Get the frequency of eso terms across all events

    """

    def __init__(self, *args, **kwargs):
        super(eso_frequency_count, self).__init__(*args, **kwargs)
        self.query_title = 'Frequency of eso types in events'
        self.description = ("eso provides an indication of the character of"
            " an event, as determined by semantic 'frames'.**This query is very slow"
            " and will timeout the server, contents are available as a file**") 
        self.url = 'eso_frequency_count'
        self.world_cup_example = 'eso_frequency_count'
        self.cars_example = 'eso_frequency_count'
        self.ft_example = 'eso_frequency_count'
        self.wikinews_example = 'eso_frequency_count'
        self.query_template = ("""
SELECT
?eso (count (?eso) AS ?count)
WHERE {{
?event a sem:Event . 
?event a ?filterfield . 
FILTER(STRSTARTS(STR(?filterfield), "http://www.newsreader-project.eu/domain-ontology")) .
BIND (?filterfield AS ?eso) .
}}
GROUP BY ?eso
ORDER by desc(?count)
LIMIT {limit}
OFFSET {offset}
                               """)

        self.count_template = ("""
SELECT
(COUNT (DISTINCT ?eso) AS ?count)
WHERE {{
?event a sem:Event . 
?event a ?filterfield . 
FILTER(STRSTARTS(STR(?filterfield), "http://www.newsreader-project.eu/domain-ontology")) .
BIND (?filterfield AS ?eso) .
}}
                               """)

        self.jinja_template = 'table.html'
        self.headers = ['eso', 'count']

        self.required_parameters = []
        self.optional_parameters = ["output", "filter"]
        self.number_of_uris_required = 0

        self.query = self._build_query()
