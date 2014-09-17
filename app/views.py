#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

import json

from flask import (render_template, request, url_for, Response, 
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

# TODO:
# 1. Wrap error responses in the appropriate manner (HTML, JSON, JSONP)
# 2. Test count queries automatically?
# 3. Generate integration tests from example URLs
# 4. Use logging instead of print statements
 
logging.basicConfig()

PER_PAGE = 20

class ViewerException(Exception):
    pass

@app.route('/')
def index():
    """ Provide documentation when accessing the root page """
    root_url = get_root_url()
    function_list = make_documentation.make_documentation(root_url)
    output = parse_query_string(request.query_string)
    if "output" not in output.keys():
        output['output'] = 'html'
    if output['output'] == 'json':
        response = make_response(json.dumps(function_list, ensure_ascii=False, sort_keys=True))
        response.headers[str('Content-type')] = str('application/json; charset=utf-8')
        response.headers[str('Access-Control-Allow-Origin')] = str('*')
        return response
    elif output['output'] == 'html':
        return render_template('index.html', help=function_list, root_url=root_url)

def parse_query_string(query_string):
    """ Return dict containing query string values.

    uris can be entered as ?uris.0=http:...&uris.1=http:... """
    try:
        parsed_query = jsonurl.parse_query(query_string)
        if "output" not in parsed_query.keys():
            parsed_query['output'] = 'html'
        return parsed_query
    except ValueError:
        raise ViewerException("Query URL is malformed")


@app.route('/<query_to_use>', defaults={'page': 1})
@app.route('/<query_to_use>/page/<int:page>')
def run_query(page, query_to_use):
    """ Return response of selected query using query string values. """
    # Try to make the query object
    query_args = {'output':'json'}
    try:
        #Assemble the query
        query_args = parse_query_string(request.query_string)
        current_query = assemble_query(query_to_use, query_args, page)
        current_query.submit_query()
        count = current_query.get_total_result_count()
    except ViewerException as e:
        print "**ViewerException"
        print e
        return produce_error_response(e, query_args)
    except queries.QueryException as e:
        return produce_error_response(e, query_args)

    return produce_response(current_query, page, query_args['offset'], count)

def assemble_query(query_to_use, query_args, page):
    try:
        query_name = getattr(queries, query_to_use)
        query_args = add_offset_and_limit(query_args, page)
        current_query = query_name(**query_args)
    except AttributeError:
        raise ViewerException('Query **{0}** does not exist'.format(query_to_use))

    return current_query

def add_offset_and_limit(query_args, page):
    if 'offset' not in query_args.keys():
        query_args['offset'] = PER_PAGE * (page - 1)
    if 'limit' not in query_args.keys():
        query_args['limit'] = PER_PAGE
    if 'callback' in query_args.keys():
        query_args['output'] = 'jsonp'
    if 'callback' not in query_args.keys():
        query_args['callback'] = None

    return query_args

def produce_error_response(e, query_args):
    try:
        tmp = query_args['output']
    except KeyError:
        query_args['output'] = 'json'

    try:
        if query_args['output'] == 'json':
            response = json.dumps({"error":e.message})
        elif query_args['output'] == 'jsonp':
            response = query_args['callback'] + '(' + e.message + ');'    
        elif query_args['output'] == 'csv':
            response = json.dumps({"error":e.message})
        elif query_args['output'] == 'html':
            response = render_template('error.html', error_message=e.message)
        else: 
            response = json.dumps({"error":e.message})
    except Exception as err:
        print "**Failed to make a proper error response"
        print type(err)
        response = ''
    return response


def produce_response(query, page_number, offset, count):
    """ Get desired result output from completed query; create a response. """

    if query.output == 'json':
        response = produce_json_response(query, page_number, count)
    elif query.output == 'jsonp':
        response = produce_jsonp_response(query, page_number, count)    
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
    response.headers[str('Content-type')] = str('application/json; charset=utf-8')
    response.headers[str('Access-Control-Allow-Origin')] = str('*')
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
    response.headers[str('Access-Control-Allow-Origin')] = str('*')
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

def produce_jsonp_response(query, page_number, count):
    response = produce_json_response(query, page_number, count)
    response.data = query.callback + '(' + response.data + ');'
    response.headers[str('Access-Control-Allow-Origin')] = str('*')
    return response

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
