#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import CRUDQuery

class get_mention_metadata(CRUDQuery):
    """ Get the metadata of a mention
    """
    # https://knowledgestore.fbk.eu/nwr/worldcup-hackathon/mentions?id=%3Chttp%3A%2F%2Fnews.bbc.co.uk%2Fsport2%2Fhi%2Ffootball%2Fgossip_and_transfers%2F5137822.stm%23char%3D1162%2C1167%26word%3Dw220%26term%3Dt220%3E
    # https://knowledgestore.fbk.eu/nwr/worldcup-hackathon/resources?id=http://news.bbc.co.uk/sport2/hi/football/gossip_and_transfers/5137822.stm 
    def __init__(self, *args, **kwargs):
        super(get_mention_metadata, self).__init__(*args, **kwargs)
        self.query_title = 'Get mention metadata'
        self.description = ('Get the metadata of a mention, including things'
            ' like links to propbank and verbnet entries and a measure of the'
            ' confidence in an event. A compact display, quite useful.'
            ' Uses the SPARQL DESCRIBE keyword which returns a network'
            ' not compatible with HTML display')
        self.url = 'get_mention_metadata'

        self.world_cup_example = 'get_mention_metadata?uris.0=http%3A%2F%2Fnews.bbc.co.uk%2Fsport2%2Fhi%2Ffootball%2Fgossip_and_transfers%2F5137822.stm%23char%3D1162%2C1167%26word%3Dw220%26term%3Dt220'
        self.cars_example = 'get_mention_metadata?uris.0=http%3A%2F%2Fwww.newsreader-project.eu%2Fdata%2Fcars%2F2003%2F01%2F04%2F47KW-0H00-01JV-737G.xml%23char%3D108%2C116'
        self.query_template = ("""{uri_0}""")
        self.count_template = ("""""")
        self.output = 'json'
        self.result_is_tabular = False
        self.action = "mentions"
        
        self.jinja_template = 'table.html'
        
        self.headers = ['**output is a graph**']

        self.required_parameters = ["uris"]
        self.optional_parameters = []
        self.number_of_uris_required = 1

        self.query = self._build_query()

    def get_total_result_count(self):
        """ Returns result count for query, exception for this describe query """
        return 0

    def parse_query_results(self):
        # TODO: nicely parsed needs defining; may depend on query
        """ Returns nicely parsed result of query. """
        return self.json_result

    def _process_input_uris(self, uris):
        if uris is not None:
            self.uris = ['%3C'+uris[0]+'%3E', None]
        else:
            self.uris = [None, None]