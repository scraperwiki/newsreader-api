#!/usr/bin/env python
# encoding: utf-8

import requests
import json

sparql_template_array = [None] * 2
sparql_template_array[0] = """
        SELECT DISTINCT ?type
        WHERE {?entity rdf:type sem:Actor .
        ?entity rdf:type ?type .}
        OFFSET %d
        LIMIT %d
        """

sparql_template_array[1] = """
        SELECT ?type (COUNT (*) as ?n)
        WHERE {
        ?a rdf:type sem:Actor .
        ?a rdf:type ?type .
        FILTER (?type != sem:Actor && STRSTARTS(STR(?type),
        "http://dbpedia.org/ontology/"))}
        GROUP BY ?type
        ORDER BY DESC(?n)
        OFFSET %d
        LIMIT %d
        """


def create_count_query():
    query = """
       SELECT (COUNT (distinct ?type) as ?n)
       WHERE {
       ?a rdf:type sem:Actor .
       ?a rdf:type ?type .
       FILTER (?type != sem:Actor && STRSTARTS(STR(?type),
       "http://dbpedia.org/ontology/"))}
       """
    return query


def create_sparql_query(sparql_template, query_index, offset=0, limit=100):
    """ Create a SPARQL query from template, using given offset and limit. """
    return sparql_template[query_index] % (offset, limit)


def perform_sparql_query(query, endpoint_url='https://knowledgestore.fbk.eu'
                                             '/nwrdemo/sparql'):
    """ Submit SPARQL query string to endpoint and return JSON result. """
    payload = {'query': query}
    response = requests.get(endpoint_url, params=payload)
    return json.loads(response.content)


def main():
    query = create_sparql_query(sparql_template_array, 1)
    print perform_sparql_query(query)


if __name__ == '__main__':
    main()
