#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

def make_documentation(root_url):
    function_list = {"description":["NewsReader Simple API: Endpoints available at this location",
                                    "",
                                    "Queries are of the form:",
                                    root_url + "{page/[n]/}query_name?param1=[string]&param2=[string]",
                                    "Where page is an option component with default /page/1",
                                    "",
                                    ""
                        ],
                     "parameters":["output={json|html|csv}",
                                   "limit",
                                   "offset",
                                   "filter",
                                   "uris.[n]",
                                   "timefilter - YYYY, YYYY-MM or YYYY-MM-DD"],
                     "prefixes":["dbo - types of things - i.e. dbo:SoccerPlayer", 
                                 "dbpedia - instances of things - i.e. dbpedia:David_Beckham"], 
                     "queries":[],
                     "resources":[]}
    function_list['queries'].append({"url":"types_of_actors",
                                   "required_parameters":[],
                                   "optional_parameters":["filter","output","offset","limit"],
                                   "example":root_url + "/types_of_actors?output=html&filter=player"})
    function_list['queries'].append({"url":"describe_uri",
                                   "parameter":["uris.0"],
                                   "optional_parameters":[],
                                   "example":root_url + "/describe_uri?uris.0=dbpedia:David_Beckham&output=json"})
    function_list['queries'].append({"url":"event_details_filtered_by_actor",
                                   "required_parameters":["uris.0"],
                                   "optional_parameters":["output","offset","limit"],                                   
                                   "example":root_url + "/event_details_filtered_by_actor?uris.0=dbpedia:David_Beckham"})
    function_list['queries'].append({"url":"actors_of_a_type",
                                   "required_parameters":["uris.0"],
                                   "optional_parameters":["filter","output","offset","limit"],
                                   "example":root_url + "/actors_of_a_type?uris.0=dbo:Person&filter=david"})
    function_list['queries'].append({"url":"property_of_actors_of_a_type",
                                   "required_parameters":["uris.0", "uris.1"],
                                   "optional_parameters":["output","offset","limit"],
                                   "example":root_url + "/property_of_actors_of_a_type?uris.0=dbo:SoccerPlayer&uris.1=dbo:height"})
    function_list['queries'].append({"url":"summary_of_events_with_actor",
                                   "required_parameters":["uris.0"],
                                   "optional_parameters":["output","offset","limit"],
                                   "example":root_url + "/summary_of_events_with_actor?uris.0=dbpedia:David_Beckham&datefilter=1999-08"})
    function_list['queries'].append({"url":"actors_sharing_event_with_an_actor",
                                   "required_parameters":["uris.0"],
                                   "optional_parameters":["datefilter","output","offset","limit"],
                                   "example":root_url + "/actors_sharing_event_with_an_actor?uris.0=dbpedia:David_Beckham"})
    function_list['queries'].append({"url":"properties_of_a_type",
                                   "required_parameters":["uris.0"],
                                   "optional_parameters":["output","offset","limit"],
                                   "example":root_url + "/properties_of_a_type?uris.0=dbo:SoccerPlayer"})
    function_list['queries'].append({"url":"summary_of_events_with_two_actors",
                                   "required_parameters":["uris.0","uris.1"],
                                   "optional_parameters":["output","offset","limit","datefilter"],
                                   "example":root_url + "/summary_of_events_with_two_actors?uris.0=dbpedia:David_Beckham&uris.1=dbpedia:Sepp_Blatter"})
    function_list['queries'].append({"url":"get_document_metadata",
                                   "required_parameters":["uris.0"],
                                   "optional_parameters":[],
                                   "example":root_url + "/get_document_metadata?uris.0=http://news.bbc.co.uk/sport2/hi/football/gossip_and_transfers/5137822.stm"})
    function_list['queries'].append({"url":"get_mention_metadata",
                                   "required_parameters":["uris.0"],
                                   "optional_parameters":[],
                                   "example":root_url + "/get_mention_metadata?uris.0=%3Chttp%3A%2F%2Fnews.bbc.co.uk%2Fsport2%2Fhi%2Ffootball%2Fgossip_and_transfers%2F5137822.stm%23char%3D1162%2C1167%26word%3Dw220%26term%3Dt220%3E"})
    function_list['queries'].append({"url":"get_document",
                                   "required_parameters":["uris.0"],
                                   "optional_parameters":[],
                                   "example":root_url + "/get_document?uris.0=http://news.bbc.co.uk/sport2/hi/football/gossip_and_transfers/5137822.stm"})
    return function_list
