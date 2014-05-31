#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import CRUDQuery

class get_mention_metadata(CRUDQuery):
    """ Get the metadata of a mention

    http://127.0.0.1:5000/get_mention_metadata?uris.0=%3Chttp%3A%2F%2Fnews.bbc.co.uk%2Fsport2%2Fhi%2Ffootball%2Fgossip_and_transfers%2F5137822.stm%23char%3D1162%2C1167%26word%3Dw220%26term%3Dt220%3E
    """
    # https://knowledgestore.fbk.eu/nwr/worldcup-hackathon/mentions?id=%3Chttp%3A%2F%2Fnews.bbc.co.uk%2Fsport2%2Fhi%2Ffootball%2Fgossip_and_transfers%2F5137822.stm%23char%3D1162%2C1167%26word%3Dw220%26term%3Dt220%3E
    # https://knowledgestore.fbk.eu/nwr/worldcup-hackathon/resources?id=http://news.bbc.co.uk/sport2/hi/football/gossip_and_transfers/5137822.stm 
    def __init__(self, *args, **kwargs):
        super(get_mention_metadata, self).__init__(*args, **kwargs)
        self.query_title = 'Get mention metadata'
        self.query_template = ("""{uri_0}""")
        self.count_template = ("""""")
        self.output = "json"
        self.action = "mentions"
        
        self.jinja_template = 'table.html'
        
        self.headers = ['property']

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

    