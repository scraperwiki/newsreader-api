#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from queries import CRUDQuery

import os
import time

from dshelpers import request_url

import requests
import json


class get_document(CRUDQuery):
    """ Get the text of a document

    http://127.0.0.1:5000/get_document?uris.0=http://news.bbc.co.uk/sport2/hi/football/gossip_and_transfers/5137822.stm
    """
    # https://knowledgestore.fbk.eu/nwr/worldcup-hackathon/mentions?id=%3Chttp%3A%2F%2Fnews.bbc.co.uk%2Fsport2%2Fhi%2Ffootball%2Fgossip_and_transfers%2F5137822.stm%23char%3D1162%2C1167%26word%3Dw220%26term%3Dt220%3E
    # https://knowledgestore.fbk.eu/nwr/worldcup-hackathon/resources?id=http://news.bbc.co.uk/sport2/hi/football/gossip_and_transfers/5137822.stm 
    def __init__(self, *args, **kwargs):
        super(get_document, self).__init__(*args, **kwargs)
        self.query_title = 'Get document'
        self.query_template = ("""{uri_0}""")
        self.count_template = ("""""")
        self.output = "json"
        self.action = "files"
        
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

    def submit_query(self, endpoint_url_stub='https://knowledgestore.fbk.eu'
                                        '/nwr/worldcup-hackathon/{action}'):
        """ Submit query to endpoint; return result. """

        username = os.environ['NEWSREADER_USERNAME']
        password = os.environ['NEWSREADER_PASSWORD']
        payload = {'id': self.query}
        
        endpoint_url = endpoint_url_stub.format(action=self.action)
        print "\n\n**New CRUD query**"
        print endpoint_url, payload
        t0 = time.time()
        try:
            response = request_url(endpoint_url, auth=(username, password),
                                   params=payload,
                                   back_off=False)
        except Exception as e:
            print "Query raised an exception"
            print type(e)
            self.error_message.append({"error":"Query raised an exception: {0}".format(type(e).__name__)})
            t1 = time.time()
            total = t1-t0
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
                self.error_message.append({"error":"Response code not OK: {0}".format(response.status_code)})

    