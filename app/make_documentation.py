#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals
import queries
from queries import PREFIX_LIBRARY

class DocsCreator(object):
    """ Creates documentation for a particular Newsreader SPARQL endpoint. """
    def __init__(self, root_url, user_api_key, endpoint_path):
        self.query_ignore_list = ['__all__', '__builtins__', '__doc__',
                                  '__file__', '__name__', '__package__',
                                  '__path__', 'queries', 'SparqlQuery',
                                  'QueryException', 'PREFIX_LIBRARY']
        self.root_url = root_url
        self.endpoint_path = endpoint_path
        self.user_api_key = user_api_key if user_api_key else '<YOUR_API_KEY>'

    # TODO: modify somewhere to include endpoint path
    def make_docs(self):
        prefixes = self._make_prefixes_from_library()
        function_list = {"description": ["",
                                         "Queries are of the form:",
                                         self.root_url + self.endpoint_path + "/query_name/{page/[n]/}?param1=[string]&param2=[string]&api_key=<YOUR_API_KEY>",
                                         "Where page is an option component with default /page/1. Note that /page/1 automatically redirects so is not seen in the URL in the browser.",
                                         "",
                                         "Vist this page with a URL of the form: " + self.root_url + self.endpoint_path + "?api_key=<YOUR_API_KEY>",
                                         "to put the API key into the example URLs",
                                         "",                                         
                                         "An API key can be obtained by contacting dataservices@scraperwiki.com",
                                         ""],
                         "parameters": ["callback = function with which to wrap response to make JSONP",
                                        "output = {json|html|csv}",
                                        "filter = a character string on which to filter, it can take combinations such as bribery+OR+bribe",
                                        "uris.[n] = a URI to a thing, e.g. dbpedia:David_Beckham",
                                        "datefilter = YYYY, YYYY-MM or YYYY-MM-DD, filter to a year, month or day",
                                        "api_key = a UUID api key, e.g. 1c867db8-a364-4f1e-a33c-e5e55775a76e",
                                        "REMOVED offset = an offset into the returned results",
                                        "REMOVED limit = a number of results to return"],
                         "prefixes": prefixes,
                         "queries": []}

        query_long_list = dir(queries)

        for query in query_long_list:
            if query in self.query_ignore_list:
                continue
            query_name = getattr(queries, query)

            query_object = query_name(offset=0, limit=100,
                                      uris=["{uri_0}", "{uri_1}"],
                                      filter='{string}',
                                      datefilter='{datefilter}', output='html')
            example_query_fragment = self._get_example_from_query(query_object)
            if "=" in example_query_fragment:
                example_query = ''.join([self.root_url, self.endpoint_path, '/',
                                    self._get_example_from_query(query_object),
                                    '&api_key=', self.user_api_key])
            else:
                example_query = ''.join([self.root_url, self.endpoint_path, '/',
                                    self._get_example_from_query(query_object),
                                    '?api_key=', self.user_api_key])

            function_list['queries'].append({
                "title": query_object.query_title,
                "description": query_object.description,
                "url": query_object.url,
                "required_parameters": query_object.required_parameters,
                "optional_parameters": query_object.optional_parameters,
                "output_columns": query_object.headers,
                "example": example_query,
                "sparql": query_object.query})
        return function_list

    @staticmethod
    def _get_example_from_query(query_object):
        raise NotImplementedError

    def _make_prefixes_from_library(self):
        prefixes = []
        for k, v in PREFIX_LIBRARY.iteritems():
            prefixes.append("{k}:   {v}".format(k=k, v=v['help']))

        prefixes.sort()
        return prefixes

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

class FTDocsCreator(DocsCreator):
    # TODO: Set self.query_ignore_list if it needs to be different.
    @staticmethod
    def _get_example_from_query(query_object):
        return query_object.ft_example

class WikiNewsDocsCreator(DocsCreator):
    # TODO: Set self.query_ignore_list if it needs to be different.
    @staticmethod
    def _get_example_from_query(query_object):
        try:
            return query_object.wikinews_example
        except:
            return query_object.cars_example