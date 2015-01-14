#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

import json

from flask import render_template, request, url_for, make_response
from app import app
from pagination import Pagination
from collections import OrderedDict
import queries
import jsonurl
import cStringIO as StringIO
import unicodecsv as csv
import logging
import urllib
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


def index(function_list):
    """ Provide documentation when accessing the root page """
    output = parse_query_string(request.query_string)
    if "output" not in output.keys():
        output['output'] = 'html'
    if output['output'] == 'json':
        response = make_response(json.dumps(
            function_list, ensure_ascii=False, sort_keys=True))
        response.headers[str('Content-type')] = str(
            'application/json; charset=utf-8')
        response.headers[str('Access-Control-Allow-Origin')] = str('*')
        return response
    elif output['output'] == 'html':
        return render_template('index.html', help=function_list)


# TODO: make_documentation and queries need to know which endpoint we're using.
# TODO: wrap these into a single function which takes DocsCreator() object
@app.route('/')
@app.route('/world_cup')
def worldcup_index():
    root_url = get_root_url()
    endpoint_path = '/world_cup'
    function_list = make_documentation.WorldCupDocsCreator(root_url, endpoint_path).make_docs()
    return index(function_list)


@app.route('/cars')
def cars_index():
    root_url = get_root_url()
    endpoint_path = '/cars'
    function_list = make_documentation.CarsDocsCreator(root_url, endpoint_path).make_docs()
    return index(function_list)


def parse_query_string(query_string):
    """ Return dict containing query string values.

    uris can be entered as ?uris.0=http:...&uris.1=http:... """
    query_string = urllib.unquote(query_string).decode('utf-8')

    print "**In parse_query_string"
    print query_string
    try:
        parsed_query = jsonurl.parse_query(query_string)
        print parsed_query
        if "output" not in parsed_query.keys():
            parsed_query['output'] = 'html'
        # Hack to escape words in Unicode strings for Virtuoso.
        # Can't just escape the whole string as e.g. "bribe OR bribery" fails.
        if "filter" in parsed_query.keys():
            filter_words = []
            for each in parsed_query['filter'].split():
                try:
                    filter_words.append(each.decode('ascii'))
                except UnicodeEncodeError:
                    filter_words.append("'" + each + "'")
            parsed_query['filter'] = ' '.join(filter_words)
        return parsed_query
    except ValueError as e:
        raise ViewerException("Query URL is malformed: {}".format(e.message))


def get_endpoint_url(api_endpoint):
    """ Take name of API endpoint as string; return KS SPARQL URL. """
    if api_endpoint == 'cars':
        knowledgestore_url = ('https://knowledgestore2.fbk.eu'
                              '/nwr/cars-hackathon/sparql')
    elif api_endpoint == 'world_cup':
        # TODO: check if this URL is  correct (though a dead link now anyway).
        knowledgestore_url = ('https://knowledgestore.fbk.eu'
                              '/nwr/worldcup-hackathon/sparql')
    return knowledgestore_url


# TODO: consider getting rid of this first line. Get query exceptions
# if you visit e.g. /foo which are a bit meaningless, it's more like a 404.
@app.route('/<query_to_use>',
           defaults={'page': 1, 'api_endpoint': 'world_cup'})
@app.route('/<api_endpoint>/<query_to_use>', defaults={'page': 1})
@app.route('/<api_endpoint>/<query_to_use>/page/<int:page>')
def run_query(page, query_to_use, api_endpoint):
    """ Return response of selected query using query string values. """
    knowledgestore_url = get_endpoint_url(api_endpoint)
    if knowledgestore_url is None:
        return render_template('error.html',
                               error_message='Endpoint not known.')
    # Try to make the query object
    query_args = {'output': 'json'}
    try:
        #Assemble the query
        print(type(query_to_use), type("get_mention_metadata"))
        if query_to_use!="get_mention_metadata":
            print "**The following line should not say get_mention_metadata"
            print query_to_use
            query_args = parse_query_string(request.query_string)
            print query_args
        else:
            print "**we are doing a special parse for get_mention_metadata**"
            query_args = parse_get_mention_metadata(request.query_string)
            print query_args

        query_args = parse_query_string(request.query_string)
        query_args['endpoint_url'] = knowledgestore_url
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

def parse_get_mention_metadata(query_string):
    parsed_query = {"output":"html", "uris":[query_string[7:]]}
    print parsed_query
    return parsed_query

def assemble_query(query_to_use, query_args, page):
    try:
        query_name = getattr(queries, query_to_use)
        query_args = add_offset_and_limit(query_args, page)
        current_query = query_name(**query_args)
    except AttributeError:
        raise ViewerException('Query **{0}** does not exist'
                              .format(query_to_use))

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
            response = json.dumps({"error": e.message})
        elif query_args['output'] == 'jsonp':
            response = query_args['callback'] + '(' + e.message + ');'
        elif query_args['output'] == 'csv':
            response = json.dumps({"error": e.message})
        elif query_args['output'] == 'html':
            response = render_template('error.html', error_message=e.message)
        else:
            response = json.dumps({"error": e.message})
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
        response = json.dumps(
            {"error": "query result cannot be written as csv"})
    response.headers[str('Access-Control-Allow-Origin')] = str('*')
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
    response.headers[str('Content-type')] = str(
        'application/json; charset=utf-8')
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
    response.headers[str('Content-type')] = str('text/csv; charset=utf-8')
    response.headers[str('Content-disposition')] = str(
        'attachment;filename='+filename)
    return response


def produce_html_response(query, page_number, count, offset):
    pagination = Pagination(page_number, PER_PAGE, int(count))
    result = query.parse_query_results()
    response = make_response(render_template(query.jinja_template,
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
                             uris=query.uris))
    return response


def produce_jsonp_response(query, page_number, count):
    response = produce_json_response(query, page_number, count)
    response.data = query.callback + '(' + response.data + ');'
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
