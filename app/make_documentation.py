#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals
import queries

def make_documentation(root_url):
    function_list = {"description":["",
                                    "Queries are of the form:",
                                    root_url + "{page/[n]/}query_name?param1=[string]&param2=[string]",
                                    "Where page is an option component with default /page/1",
                                    "",
                                    ""
                        ],
                     "parameters":["output = {json|html|csv}",
                                   "limit = a number of results to return",
                                   "offset = an offset into the returned results",
                                   "filter = a character string on which to filter, it can take combinations such as bribery+OR+bribe",
                                   "uris.[n] = a URI to a thing, e.g. dbpedia:David_Beckham",
                                   "datefilter = YYYY, YYYY-MM or YYYY-MM-DD, filter to a year, month or day"],
                     "prefixes":["dbo - types of things - i.e. dbo:SoccerPlayer", 
                                 "dbpedia - instances of things - i.e. dbpedia:David_Beckham",
                                 "framenet - NewsReader link to FrameNet semantic frames",
                                 "gaf - Grounded Annotation Framework, just contains gaf:denotedBy which references mentions", 
                                 "rdf - Resource Description Framework",
                                 "rdfs - RDF Schema",
                                 "sem - semanticweb, key to the NewsReader technology"], 
                     "queries":[]}

    query_long_list = dir(queries)
    reject_list = ['__all__', '__builtins__', '__doc__', '__file__', '__name__',
                   '__package__', '__path__', 'queries']

    for query in query_long_list:
        if query in reject_list:
            continue
        query_name = getattr(queries, query)
        query_object = query_name(offset=0, limit=100, uris=["{uri_0}", "{uri_1}"], filter='{string}', datefilter='{datefilter}', output='html')
        function_list['queries'].append({
                                   "title": query_object.query_title,
                                   "description": query_object.description,
                                   "url": query_object.url,
                                   "required_parameters":query_object.required_parameters,
                                   "optional_parameters":query_object.optional_parameters,
                                   "output_columns":query_object.headers,
                                   "example":root_url + '/' + query_object.example,
                                   "sparql": query_object.query})
    return function_list

