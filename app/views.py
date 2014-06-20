#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

import json

from flask import (abort, render_template, request, url_for, Response, 
                   make_response)
from app import app
from pagination import Pagination
from collections import OrderedDict
import queries
import jsonurl
import cStringIO as StringIO
import unicodecsv as csv
import logging
from app import make_documentation

logging.basicConfig()

PER_PAGE = 20

@app.route('/')
def index():
    """ Provide documentation when accessing the root page """
    root_url = get_root_url()
    function_list = make_documentation.make_documentation(root_url)
    output = parse_query_string(request.query_string)
    if "output" not in output.keys():
        output['output'] = 'html'
    if output['output'] == 'json':
        help = json.dumps(function_list, ensure_ascii=False, sort_keys=True)
        return Response(help, content_type=str('application/json; charset=utf-8'))
    elif output['output'] == 'html':
        return render_template('index.html', help=function_list, root_url=root_url)

def parse_query_string(query_string):
    """ Return dict containing query string values.

    uris can be entered as ?uris.0=http:...&uris.1=http:... """
    try:
        return jsonurl.parse_query(query_string)
    except ValueError:
        return {"error":"Malformed query URL"}


@app.route('/<query_to_use>', defaults={'page': 1})
@app.route('/<query_to_use>/page/<int:page>')
def run_query(page, query_to_use):
    """ Return response of selected query using query string values. """
    # Try to make the query object
    try:
        query_name = getattr(queries, query_to_use)
    except AttributeError:
        missing_query_response = []
        missing_query_response.append({"error":"Query '{0}' does not exist".format(query_to_use)})
        missing_query_response.append({"message":["For available queries, see here:",
                                        get_root_url()]})
        error_message_json = json.dumps(missing_query_response) 
        return error_message_json
    # Process the other arguments
    query_args = parse_query_string(request.query_string)

    if "error" in query_args.keys():
        error_message_json = json.dumps(query_args)
        return error_message_json

    query_args = add_offset_and_limit(query_args, page)

    #Add the arguments to the query
    current_query = query_name(**query_args)

    if len(current_query.error_message) != 0:
        error_message_json = json.dumps(current_query.error_message)
        return error_message_json

    #Make the query
    current_query.submit_query()

    #Check the query response for error states
    if len(current_query.error_message) != 0:
        error_message_json = json.dumps(current_query.error_message)
        return error_message_json               
    
    if not current_query.parse_query_results() and page != 1:
        error_message_json = json.dumps({"error":"No results, probably a request for an invalid page number"})
        return error_message_json
    #Return query response if all is well
    return produce_response(current_query, page, query_args['offset'])

def add_offset_and_limit(query_args, page):
    if 'offset' not in query_args.keys():
        query_args['offset'] = PER_PAGE * (page - 1)
    if 'limit' not in query_args.keys():
        query_args['limit'] = PER_PAGE 

    return query_args

def produce_response(query, page_number, offset):
    """ Get desired result output from completed query; create a response. """
    # TODO: avoid calling count more than once, expensive (though OK if cached)

    try:
        count = query.get_total_result_count()
    except:
        error_message_json = json.dumps(query.error_message)
        return error_message_json
        

    if query.output == 'json':
        response = produce_json_response(query, page_number, count)   
    elif query.output == 'csv' and query.result_is_tabular:
        response = produce_csv_response(query, page_number, count)
    elif query.output == 'html':
        response = produce_html_response(query, page_number, count, offset)
    else: 
        response = json.dumps({"error":"query result cannot be written as csv"})
    return response

def produce_json_response(query, page_number, count):
    root_url = get_root_url()
    pagination = Pagination(page_number, PER_PAGE, int(count))
    output = {}
    output['payload'] = query.clean_json
    output['count'] = count
    output['page number'] = page_number
    output['next page'] = root_url + url_for_other_page(pagination.page + 1)
    response = make_response(json.dumps(output, sort_keys=True))
    response.headers[str('Content-type')]=str('application/json; charset=utf-8')
    return response

def produce_csv_response(query, page_number, count):
    output = StringIO.StringIO()
    fieldnames = OrderedDict(zip(query.headers, 
                            [None]*len(query.headers)))
    dw = csv.DictWriter(output, fieldnames=fieldnames)
    dw.writeheader()
    for row in query.clean_json:
        dw.writerow(row)

    filename = 'results-page-{0}.csv'.format(page_number)
    response = make_response(output.getvalue())
    response.headers[str('Content-type')]=str('text/csv; charset=utf-8')
    response.headers[str('Content-disposition')]=str('attachment;filename='+filename)
    return response

def produce_html_response(query, page_number, count, offset):
    pagination = Pagination(page_number, PER_PAGE, int(count))
    result = query.parse_query_results()
    return render_template(query.jinja_template,
                           title=query.query_title,
                           pagination=pagination,
                           query=query.query,
                           count=count,
                           headers=query.headers,
                           results=result, 
                           offset=offset+1,
                           filter=query.filter,
                           query_time=query.query_time,
                           count_time=query.count_time,
                           datefilter=query.datefilter,
                           uris=query.uris)

def produce_jsonp_response():
    pass

def url_for_other_page(page):
    args = dict(request.view_args.items() + request.args.to_dict().items())
    args['page'] = page
    return url_for(request.endpoint, **args)

def get_root_url():
    if app.config['DEBUG']:
        root_url = "http://127.0.0.1:5000"
    else:
        root_url = "https://newsreader.scraperwiki.com"
    return root_url

app.jinja_env.globals['url_for_other_page'] = url_for_other_page
