#!/usr/bin/env python
# encoding: utf-8
from flask import render_template, request
from app import app
from collections import namedtuple
import query3


@app.route('/')
def index():
    """ Demo function. """
    return "Hello World!"


def get_offset_and_limit_from_query():
    """ Return offset and limit from query. """
    return request.args.get('offset'), request.args.get('limit')


@app.route('/simple/query3')
def handle_offset_and_limit():
    """ Simple query string function. """
    offset, limit = get_offset_and_limit_from_query()
    return render_template("query3.html", title='Query 3 test query string',
                           offset=offset, limit=limit)


@app.route('/test/query3')
def run_test_query():
    offset, limit = get_offset_and_limit_from_query()

    query = query3.create_sparql_query(query3.sparql_template_array, 1)
    json_query_results = query3.perform_sparql_query(query)
    parsed_results = parse_query3_results(json_query_results)

    result_count = get_query_3_result_count()
    return render_template("parsed_query3.html", title='Query 3 results',
                            count=result_count, results=parsed_results)


def get_query_3_result_count():
    json_count_result = \
        query3.perform_sparql_query(query3.create_count_query())
    return json_count_result['results']['bindings'][0]['n']['value']


def parse_query3_results(json_query_results):
    Query3Result = namedtuple('Query3Result', 'entity_type count')
    results = []
    for result in json_query_results['results']['bindings']:
        entity_type = result['type']['value']
        count = result['n']['value']
        results.append(Query3Result(entity_type, count))
    return results
