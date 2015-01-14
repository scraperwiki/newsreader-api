#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals
import queries


class DocsCreator(object):
    """ Creates documentation for a particular Newsreader SPARQL endpoint. """
    def __init__(self, root_url, endpoint_path=''):
        self.query_ignore_list = ['__all__', '__builtins__', '__doc__',
                                  '__file__', '__name__', '__package__',
                                  '__path__', 'queries', 'SparqlQuery',
                                  'QueryException']
        self.root_url = root_url
        self.endpoint_path = endpoint_path

    # TODO: modify somewhere to include endpoint path
    def make_docs(self):
        function_list = {"description": ["",
                                         "Queries are of the form:",
                                         self.root_url + self.endpoint_path + "/query_name/{page/[n]/}?param1=[string]&param2=[string]",
                                         "Where page is an option component with default /page/1",
                                         "",
                                         ""],
                         "parameters": ["callback = function with which to wrap response to make JSONP",
                                        "output = {json|html|csv}",
                                        "limit = a number of results to return",
                                        "offset = an offset into the returned results",
                                        "filter = a character string on which to filter, it can take combinations such as bribery+OR+bribe",
                                        "uris.[n] = a URI to a thing, e.g. dbpedia:David_Beckham",
                                        "datefilter = YYYY, YYYY-MM or YYYY-MM-DD, filter to a year, month or day"],
                         "prefixes": ["dbo - types of things - i.e. dbo:SoccerPlayer",
                                      "dbpedia - instances of things - i.e. dbpedia:David_Beckham",
                                      "framenet - NewsReader link to FrameNet semantic frames",
                                      "gaf - Grounded Annotation Framework, just contains gaf:denotedBy which references mentions",
                                      "rdf - Resource Description Framework",
                                      "rdfs - RDF Schema",
                                      "sem - semanticweb, key to the NewsReader technology"],
                         "queries": []}

        query_long_list = dir(queries)

        for query in query_long_list:
            if query in self.query_ignore_list:
                continue
            print query
            query_name = getattr(queries, query)
            query_object = query_name(offset=0, limit=100,
                                      uris=["{uri_0}", "{uri_1}"],
                                      filter='{string}',
                                      datefilter='{datefilter}', output='html')
            function_list['queries'].append({
                "title": query_object.query_title,
                "description": query_object.description,
                "url": query_object.url,
                "required_parameters": query_object.required_parameters,
                "optional_parameters": query_object.optional_parameters,
                "output_columns": query_object.headers,
                "example": self.root_url + '/' + self._get_example_from_query(query_object),
                "sparql": query_object.query})
        return function_list

    @staticmethod
    def _get_example_from_query(query_object):
        raise NotImplementedError


class WorldCupDocsCreator(DocsCreator):
    # TODO: Set self.query_ignore_list if it needs to be different.
    @staticmethod
    def _get_example_from_query(query_object):
        return query_object.world_cup_example


class CarsDocsCreator(DocsCreator):
    # TODO: Set self.query_ignore_list if it needs to be different.
    @staticmethod
    def _get_example_from_query(query_object):
        return query_object.cars_example
