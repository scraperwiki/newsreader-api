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


@app.route('/simple/query3')
def handle_offset_and_limit():
    """ Simple query string function. """
    offset = request.args.get('offset')
    limit = request.args.get('limit')
    return render_template("query3.html", title='Query 3', offset=offset,
                           limit=limit)


@app.route('/test/query3')
def run_test_query():
    query = query3.create_sparql_query(query3.sparql_template_array, 1)
    json_query_results = query3.perform_sparql_query(query)
    parsed_results = parse_query3_results(json_query_results)
    return render_template("parsed_query3.html", title='Query 3 results',
                           results=parsed_results)


def parse_query3_results(json_query_results):
    Query3Result = namedtuple('Query3Result', 'entity_type count')
    results = []
    for result in json_query_results['results']['bindings']:
        entity_type = result['type']['value']
        count = result['n']['value']
        results.append(Query3Result(entity_type, count))
    return results
