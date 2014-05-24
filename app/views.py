#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

import json

from flask import abort, render_template, request, url_for, Response
from app import app
from pagination import Pagination
from collections import OrderedDict
import queries
import jsonurl
import io
import csv

PER_PAGE = 20


@app.route('/')
def index():
    """ Provide documentation when accessing the root page """
    function_list = {"description":"NewsReader Simple API: Endpoints available at this location",
                     "global parameters":"output={json|html}", 
                     "links":[]}
    function_list['links'].append({"url":"entities_that_are_actors",
                                   "parameter":"filter",
                                   "example":"http://127.0.0.1:5000/entities_that_are_actors?output=json&filter=player"})
    function_list['links'].append({"url":"describe_uri",
                                   "parameter":"uris.0",
                                   "example":"http://127.0.0.1:5000/describe_uri?uris.0=http://dbpedia.org/resource/David_Beckham&output=json"})
    function_list['links'].append({"url":"GetEventDetailsByActorUri",
                                   "parameter":"uris.0",
                                   "example":"http://127.0.0.1:5000/GetEventDetailsByActorUri?uris.0=http://dbpedia.org/resource/David_Beckham&output=json"})
    function_list['links'].append({"url":"actors_of_a_type",
                                   "parameters":"uris.0, filter",
                                   "example":"http://127.0.0.1:5000/actors_of_a_type?uris.0=http://dbpedia.org/ontology/Person&output=json&filter=david"})
    help = json.dumps(function_list, ensure_ascii=False, sort_keys=True)
    return Response(help, content_type='application/json; charset=utf-8')


def parse_query_string(query_string):
    """ Return dict containing query string values.

    uris can be entered as ?uris.0=http:...&uris.1=http:... """
    return jsonurl.parse_query(query_string)


@app.route('/<query_to_use>', defaults={'page': 1})
@app.route('/<query_to_use>/page/<int:page>')
def run_query(page, query_to_use):
    """ Return response of selected query using query string values. """
    query_name = getattr(queries, query_to_use)
    query_args = parse_query_string(request.query_string)

    offset = PER_PAGE * (page - 1)
    current_query = query_name(offset=offset, limit=PER_PAGE, **query_args)
    current_query.submit_query()

    cause_404_if_no_results(current_query.parse_query_results(), page)
    return produce_response(current_query, page, offset)


def produce_response(query, page_number, offset):
    """ Get desired result output from completed query; create a response. """
    # TODO: avoid calling count more than once, expensive (though OK if cached)
    if query.output == 'json':
        return json.dumps(query.clean_json)
    elif query.output == 'csv':
        if query.result_is_tabular:
            output = io.StringIO()
            fieldnames = OrderedDict(zip(query.headers, 
                                    [None]*len(query.headers)))
            dw = csv.DictWriter(output, fieldnames=fieldnames)
            print fieldnames
            dw.writeheader()
            for row in query.clean_json:
                print row
                dw.writerow(row)
            return dw.getvalue()
        else:
            return json.dumps({"Error":"query result cannot be written as csv"})
    else:
        count = query.get_total_result_count()
        pagination = Pagination(page_number, PER_PAGE, int(count))
        result = query.parse_query_results()
        return render_template(query.jinja_template,
                               title=query.query_title,
                               pagination=pagination,
                               query=query.query,
                               count=count,
                               headers=query.headers,
                               results=result, offset=offset+1)


def cause_404_if_no_results(results, page_number):
    """ If results is an empty string or None, cause 404. """
    # TODO: Look into this; doesn't seem to apply for the SPARQL responses.
    if not results and page_number != 1:
        abort(404)


def url_for_other_page(page):
    args = dict(request.view_args.items() + request.args.to_dict().items())
    args['page'] = page
    return url_for(request.endpoint, **args)

app.jinja_env.globals['url_for_other_page'] = url_for_other_page
