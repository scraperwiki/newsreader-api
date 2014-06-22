#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import CRUDQuery

class get_document_metadata(CRUDQuery):
    """ Get the metadata of a document

    http://127.0.0.1:5000/get_document_metadata?uris.0=<uri>
    """
    # https://knowledgestore.fbk.eu/nwr/worldcup-hackathon/resources?id=http://news.bbc.co.uk/sport2/hi/football/gossip_and_transfers/5137822.stm 
    def __init__(self, *args, **kwargs):
        super(get_document_metadata, self).__init__(*args, **kwargs)
        self.query_title = 'Get document metadata'
        self.description = ('Get the metadata of a document, this includes title'
            ' and author where available and also a list of all the "mentions" '
            'it contains, which can be lengthy and not necessarily informative.'
            ' It uses the SPARQL DESCRIBE keyword which returns'
            ' a network not compatible with HTML display.')
        self.url = 'get_document_metadata'
        self.example = 'get_document_metadata?uris.0=http://news.bbc.co.uk/sport2/hi/football/gossip_and_transfers/5137822.stm'
        self.query_template = ("""{uri_0}""")
        self.count_template = ("""""")
        self.result_is_tabular = False
        self.action = "resources"
        
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

    