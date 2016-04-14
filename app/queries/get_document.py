#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import CRUDQuery, QueryException
import os
import time

import requests
import json


class get_document(CRUDQuery):
    """ Get the text of a document

    http://127.0.0.1:5000/get_document?uris.0=http://news.bbc.co.uk/sport2/hi/football/gossip_and_transfers/5137822.stm
    """
    # https://knowledgestore.fbk.eu/nwr/worldcup-hackathon/mentions?id=%3Chttp%3A%2F%2Fnews.bbc.co.uk%2Fsport2%2Fhi%2Ffootball%2Fgossip_and_transfers%2F5137822.stm%23char%3D1162%2C1167%26word%3Dw220%26term%3Dt220%3E
    # https://knowledgestore.fbk.eu/nwr/worldcup-hackathon/resources?id=http://news.bbc.co.uk/sport2/hi/football/gossip_and_transfers/5137822.stm 
    def __init__(self, endpoint_url=None, *args, **kwargs):
        super(get_document, self).__init__(*args, **kwargs)
        self.query_title = 'Get the text of a document'
        self.description = ('Get the text of a document from the CRUD endpoint,'
            ' where it is available. This excludes LexisNexis material')
        self.url = 'get_document'
        self.world_cup_example = 'get_document?uris.0=http://news.bbc.co.uk/sport2/hi/football/gossip_and_transfers/5137822.stm'
        self.cars_example = 'get_document?uris.0=http://news.bbc.co.uk/sport2/hi/football/gossip_and_transfers/5137822.stm'
        self.ft_example = 'get_document?uris.0=http://www.newsreader-project.eu/data/2013/10/312013/10/312013/10/31/11779884.xml'
        self.wikinews_example = 'get_document?uris.0=http://en.wikinews.org/wiki/Obama,_Romney_spar_in_first_2012_U.S._presidential_debate'
        self.query_template = ("""{uri_0}""")
        self.count_template = ("""""")
        self.endpoint_stub_url = endpoint_url
        self.output = 'json'
        self.result_is_tabular = False
        self.action = "files"
        
        self.jinja_template = 'table.html'
        
        self.headers = ['content']

        self.required_parameters = ["uris"]
        self.optional_parameters = []
        self.number_of_uris_required = 1

        self.query = self._build_query()

    def get_total_result_count(self, *args, **kwargs):
        """ Returns result count for query, exception for this describe query """
        return 0

    def parse_query_results(self):
        # TODO: nicely parsed needs defining; may depend on query
        """ Returns nicely parsed result of query. """
        return self.json_result

    def submit_query(self, username, password):
        """ Submit query to endpoint; return result. """

        #username = os.environ['NEWSREADER_USERNAME']
        #password = os.environ['NEWSREADER_PASSWORD']
        payload = {'id': self.query}
        
        endpoint_url = self.endpoint_stub_url.format(action=self.action)
        print "\n\n**New CRUD query**"
        print endpoint_url, payload
        t0 = time.time()
        try:
            response = requests.get(endpoint_url, auth=(username, password),
                                    params=payload)
        except Exception as e:
            print "Query raised an exception"
            print type(e)
            t1 = time.time()
            total = t1-t0
            raise QueryException("Query raised an exception: {0}".format(type(e).__name__))
        else:
            t1 = time.time()
            total = t1-t0
            print "Time to return from query: {0:.2f} seconds".format(total)
            print "Response code: {0}".format(response.status_code)
            print "From cache: {0}".format(response.from_cache)

            #print response.content
            
            if response and (response.status_code == requests.codes.ok):
                self.json_result = {"content":response.content}
                self.clean_json = self.json_result
            else:
                raise QueryException("Response code not OK: {0}".format(response.status_code))

    
