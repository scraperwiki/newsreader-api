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
        self.query_template = ("""{uri_0}""")
        self.count_template = ("""""")
        self.action = "resources"
        
        self.jinja_template = 'table.html'
        
        self.headers = ['property']

        self.required_parameters = ["uris"]
        self.optional_parameters = []
        self.number_of_uris_required = 1

        self.query = self._build_query()

    