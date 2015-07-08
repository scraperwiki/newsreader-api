#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals, division

import json

from flask import (abort, render_template, request, url_for, make_response,
                   send_from_directory)
from app import app
from pagination import Pagination
from collections import namedtuple, OrderedDict
import functools
import queries
import jsonurl
import cStringIO as StringIO
import unicodecsv as csv
import logging
import math
import os
import urllib
from app import make_documentation

# TODO:
# 1. Wrap error responses in the appropriate manner (HTML, JSON, JSONP)
# 2. Test count queries automatically?
# 3. Generate integration tests from example URLs
# 4. Use logging instead of print statements

logging.basicConfig()

PER_PAGE = 20
DEFAULT_ENDPOINT = 'cars'


class ViewerException(Exception):
    pass


def validate_api_key(api_key, endpoint):
    public_api_keys = os.environ['NEWSREADER_PUBLIC_API_KEY'].split(',')
    private_api_keys = os.environ['NEWSREADER_PRIVATE_API_KEY'].split(',')

    validated = False
    if endpoint == 'dutchhouse' and api_key in private_api_keys:
        validated = True
    elif endpoint in ['cars', 'worldcup'] and api_key in public_api_keys:
        validated = True
    return validated


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


# TODO: wrap these into a single function which takes DocsCreator() object
@app.route('/')
@app.route('/cars')
def cars_index():
    root_url = get_root_url()
    endpoint_path = '/cars'
    user_api_key = request.args.get('api_key')
    function_list = make_documentation.CarsDocsCreator(root_url, user_api_key,
                                                       endpoint_path).make_docs()
    return index(function_list)


@app.route('/world_cup')
def worldcup_index():
    root_url = get_root_url()
    endpoint_path = '/world_cup'
    user_api_key = request.args.get('api_key')
    function_list = make_documentation.WorldCupDocsCreator(root_url,
                                                           user_api_key,
                                                           endpoint_path).make_docs()
    return index(function_list)

@app.route('/dutchhouse')
def dutchhouse_index():
    root_url = get_root_url()
    endpoint_path = '/dutchhouse'
    user_api_key = request.args.get('api_key')
    function_list = make_documentation.DutchHouseDocsCreator(root_url, user_api_key,
                                                       endpoint_path).make_docs()
    return index(function_list)

def parse_query_string(query_string):
    """ Return dict containing query string values.

    uris can be entered as ?uris.0=http:...&uris.1=http:... """
    query_string = urllib.unquote(query_string).decode('utf-8')

    try:
        parsed_query = jsonurl.parse_query(query_string)
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


def get_endpoint_credentials(api_endpoint):
    """ Take name of API endpoint as string; return KS SPARQL URL. """
    Credentials = namedtuple("Credentials", "url username password")
    url = ('https://knowledgestore2.fbk.eu/nwr/cars-hackathon/{action}')
    username = os.environ.get('NEWSREADER_PUBLIC_USERNAME')
    password = os.environ.get('NEWSREADER_PUBLIC_PASSWORD')

    if api_endpoint == 'world_cup':
        # TODO: check if this URL is  correct (though a dead link now anyway).
        url = ('https://knowledgestore.fbk.eu'
               '/nwr/worldcup-hackathon/{action}')
    elif api_endpoint == 'dutchhouse':
        url = ('https://knowledgestore2.fbk.eu'
               '/nwr/dutchhouse-v2/{action}')
        username = os.environ.get('NEWSREADER_PRIVATE_USERNAME')
        password = os.environ.get('NEWSREADER_PRIVATE_PASSWORD')

    return Credentials(url, username, password)


# TODO: consider getting rid of this first line. Get query exceptions
# if you visit e.g. /foo which are a bit meaningless, it's more like a 404.
@app.route('/<query_to_use>',
           defaults={'page': 1, 'api_endpoint': DEFAULT_ENDPOINT})
@app.route('/<query_to_use>/page/<int:page>',
           defaults={'api_endpoint': DEFAULT_ENDPOINT})
@app.route('/<api_endpoint>/<query_to_use>', defaults={'page': 1})
@app.route('/<api_endpoint>/<query_to_use>/page/<int:page>')
def run_query(page, query_to_use, api_endpoint):
    """ Return response of selected query using query string values. """
    if not validate_api_key(request.args.get('api_key', None), api_endpoint):
        abort(401)

    ks_credentials = get_endpoint_credentials(api_endpoint)
    if ks_credentials.url is None:
        return render_template('error.html',
                               error_message='Endpoint not known.',
                               root_url=get_root_url())
    # Try to make the query object
    query_args = {'output': 'json'}
    try:
        #Assemble the query
        if query_to_use!="get_mention_metadata":
            query_args = parse_query_string(request.query_string)
        else:
            print "**we are doing a special parse for get_mention_metadata**"
            query_args = parse_get_mention_metadata(request.query_string)
            print query_args

        query_args['endpoint_url'] = ks_credentials.url
        current_query = assemble_query(query_to_use, query_args, page)
        current_query.submit_query(ks_credentials.username,
                                   ks_credentials.password)
        count = current_query.get_total_result_count(ks_credentials.username,
                                                     ks_credentials.password)

        if count > 0 and final_page_exceeded(count, page):
            raise ResultPageLimitExceededException(
                "Exceeded final result page.")


    except (ViewerException, queries.QueryException,
            ResultPageLimitExceededException) as e:
        return produce_error_response(e, query_args)
    else:
        return produce_response(current_query, page, query_args['offset'],
                                count)


class ResultPageLimitExceededException(Exception):
    pass


def final_page_exceeded(count, page_number):
    """ Return True if we have gone past the final page of results.

    Needed because SPARQL will return the final page of results, even if the
    offset goes beyond the count.
    """
    return page_number > int(math.ceil(count/PER_PAGE))


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
    if 'offset' in query_args.keys():
        logging.warning("Ignoring user supplied offset")
    if 'limit' in query_args.keys():
        logging.warning("Ignoring user supplied limit")
    #if 'offset' not in query_args.keys():
    query_args['offset'] = PER_PAGE * (page - 1)
    #if 'limit' not in query_args.keys():
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
            response = render_template('error.html', 
                                        error_message=e.message,
                                        root_url=get_root_url())
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

    if pagination.has_next:
        output['next page'] = (root_url +
                               url_for_other_page(pagination.page + 1))

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
                             uris=query.uris,
                             root_url=get_root_url()))
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
