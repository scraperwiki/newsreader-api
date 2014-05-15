#!/usr/bin/env python
# encoding: utf-8
from flask import render_template, request
from app import app
from collections import namedtuple
from views import get_query_3_result_count, parse_query3_results
import query3


def get_offset_and_limit_from_query():
    """ Return offset and limit from query. """
    try:
        offset = int(request.args.get('offset'))
    except TypeError:
        offset = 0

    try:
        limit = int(request.args.get('limit'))
    except TypeError:
        limit = 100

    return offset, limit


@app.route('/simple/query3')
def handle_offset_and_limit():
    """ Simple query string function. """
    offset, limit = get_offset_and_limit_from_query()
    return render_template("query3.html", title='Query 3 test query string',
                           offset=offset, limit=limit)


@app.route('/test/query3')
def run_test_query():
    offset, limit = get_offset_and_limit_from_query()
    result_start_number = offset + 1
    query = query3.create_sparql_query(query3.sparql_template_array, 1,
                                       offset, limit)
    json_query_results = query3.perform_sparql_query(query)
    parsed_results = parse_query3_results(json_query_results)

    result_count = get_query_3_result_count()
    return render_template("parsed_query3.html", title='Query 3 results',
                           count=result_count, results=parsed_results,
                           result_start_number=result_start_number)
