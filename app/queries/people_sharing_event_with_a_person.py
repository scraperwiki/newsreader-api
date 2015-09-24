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
        self.world_cup_example = 'people_sharing_event_with_a_person?uris.0=dbpedia:David_Beckham'
        self.cars_example = 'people_sharing_event_with_a_person?uris.0=dbpedia:Alan_Mulally'
        self.dutchhouse_example = 'people_sharing_event_with_a_person?uris.0=dbpedianl:Rijkman_Groenink'
        self.wikinews_example = 'people_sharing_event_with_a_person?uris.0=dbpedia:Barack_Obama'
        self.query_template = ("""
SELECT ({uri_0} AS ?actor) ?actor2
       (COUNT(DISTINCT ?evt) as ?numEvent) ?comment
WHERE {{
  ?evt sem:hasActor {uri_0} , ?actor2 .
  ?actor2 a dbo:Person .
  FILTER(?actor2 != {uri_0})
  OPTIONAL {{ ?actor2 rdfs:comment ?comment }}
}}
GROUP BY ?actor2 ?comment
ORDER BY DESC(?numEvent)
OFFSET {offset}
LIMIT {limit}
                               """)

        self.count_template = ("""
SELECT (COUNT(DISTINCT ?actor2) as ?count)
WHERE {{
  ?evt sem:hasActor {uri_0} , ?actor2 .
  ?actor2 a dbo:Person .
  FILTER(?actor2 != {uri_0})
}}
                               """)

        self.jinja_template = 'table.html'
        self.headers = ['actor', 'actor2', 'numEvent', 'comment']

        self.required_parameters = ["uris"]
        self.optional_parameters = ["output", "offset", "limit"]
        self.number_of_uris_required = 1

        self.query = self._build_query()
