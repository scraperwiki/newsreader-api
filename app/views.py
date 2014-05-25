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

PER_PAGE = 20

@app.route('/')
def index():
    """ Provide documentation when accessing the root page """
    if app.config['DEBUG']:
        root_url = "http://127.0.0.1:5000"
    else:
        root_url = "https://newsreader.scraperwiki.com"
    
    function_list = {"description":"NewsReader Simple API: Endpoints available at this location",
                     "global parameters":"output={json|html|csv}",
                     "known prefix 1":"dbo - types of things - i.e. dbo:SoccerPlayer", 
                     "known prefix 2":"dbpedia - instances of things - i.e. dbpedia:David_Beckham", 
                     "links":[]}
    function_list['links'].append({"url":"types_of_actors",
                                   "parameter":"filter",
                                   "example":root_url + "/types_of_actors?output=html&filter=player"})
    function_list['links'].append({"url":"describe_uri",
                                   "parameter":"uris.0",
                                   "example":root_url + "/describe_uri?uris.0=dbpedia:David_Beckham&output=json"})
    function_list['links'].append({"url":"event_details_filtered_by_actor",
                                   "parameter":"uris.0",
                                   "example":root_url + "/event_details_filtered_by_actor?uris.0=dbpedia:David_Beckham&output=json"})
    function_list['links'].append({"url":"actors_of_a_type",
                                   "parameters":"uris.0, filter",
                                   "example":root_url + "/actors_of_a_type?uris.0=dbo:Person&output=json&filter=david"})
    function_list['links'].append({"url":"property_of_actors_of_a_type",
                                   "parameters":"uris.0, uris.1",
                                   "example":root_url + "/property_of_actors_of_a_type?uris.0=dbo:SoccerPlayer&uris.1=dbo:height"})

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
    print query_args
    offset = PER_PAGE * (page - 1)
    current_query = query_name(offset=offset, limit=PER_PAGE, **query_args)
    current_query.submit_query()

    cause_404_if_no_results(current_query.parse_query_results(), page)
    return produce_response(current_query, page, offset)


def produce_response(query, page_number, offset):
    """ Get desired result output from completed query; create a response. """
    # TODO: avoid calling count more than once, expensive (though OK if cached)
    print query.query
    if app.config['DEBUG']:
        root_url = "http://127.0.0.1:5000"
    else:
        root_url = "https://newsreader.scraperwiki.com"
    if query.output == 'json':
        count = query.get_total_result_count()
        pagination = Pagination(page_number, PER_PAGE, int(count))
        output = {}
        output['payload'] = query.clean_json
        output['count'] = count
        output['page number'] = page_number
        output['next page'] = root_url + url_for_other_page(pagination.page + 1)
        return json.dumps(output, sort_keys=True)
    elif query.output == 'csv':
        if query.result_is_tabular:
            output = StringIO.StringIO()
            fieldnames = OrderedDict(zip(query.headers, 
                                    [None]*len(query.headers)))
            dw = csv.DictWriter(output, fieldnames=fieldnames)
            dw.writeheader()
            for row in query.clean_json:
                dw.writerow(row)

            filename = 'results-page-{0}.csv'.format(page_number)
            response = make_response(output.getvalue())
            response.headers['Content-type']='text/csv; charset=utf-8'
            response.headers['Content-disposition']='attachment;filename='+filename
            return response
            #return Response(output.getvalue(), 
            #  content_type='text/csv; charset=utf-8',
            #  content_disposition='attachment;filename=results.csv')
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
