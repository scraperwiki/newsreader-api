#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import SparqlQuery

class people_sharing_event_with_a_person(SparqlQuery):

    """ Get people sharing an event with a named person with count of occurence
    """

    def __init__(self, *args, **kwargs):
        super(people_sharing_event_with_a_person,
              self).__init__(*args, **kwargs)
        self.query_title = 'People who share an event with a named person'
        self.description = 'Gets the people who share an event with a named person, counts the number of such events and displays in descending order'
        self.url = 'people_sharing_event_with_a_person'
        self.example = 'people_sharing_event_with_a_person?uris.0=dbpedia:David_Beckham'
        self.query_template = ("""
SELECT DISTINCT ?actor ?actor2 (COUNT(?evt) as ?numEvent) ?comment
WHERE {{
?evt a sem:Event .
?evt sem:hasActor ?actor .
?evt sem:hasActor ?actor2 .
?actor2 a dbo:Person . 
FILTER(?actor = {uri_0} && ?actor2 != ?actor) . 
?actor2 rdfs:comment ?comment .
}}
GROUP BY ?actor2 ?actor ?comment
ORDER BY DESC(?numEvent)
OFFSET {offset}
LIMIT {limit}
                               """)

        self.count_template = ("""
SELECT (COUNT (DISTINCT ?actor2) as ?count)
WHERE {{
?evt a sem:Event .
?evt sem:hasActor ?actor .
?evt sem:hasActor ?actor2 .
?actor2 a dbo:Person . 
FILTER(?actor = {uri_0} && ?actor2 != ?actor) . 
?actor2 rdfs:comment ?comment .
}}
                               """)

        self.jinja_template = 'table.html'
        self.headers = ['actor', 'actor2', 'numEvent', 'comment']

        self.required_parameters = ["uris"]
        self.optional_parameters = ["output", "offset", "limit"]
        self.number_of_uris_required = 1

        self.query = self._build_query()
