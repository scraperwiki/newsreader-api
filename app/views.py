#!/usr/bin/env python
# encoding: utf-8
import json

from flask import abort, render_template, request, url_for
from app import app
from pagination import Pagination
import queries

PER_PAGE = 10


@app.route('/')
def index():
    """ Demo function. """
    return "Hello World!"


@app.route('/<query_to_use>', defaults={'page': 1})
@app.route('/<query_to_use>/page/<int:page>')
def run_query(page, query_to_use):
    """ Return response of selected query using query string values. """
    query_name = getattr(queries, query_to_use)
    query_args = parse_query_string(**request.args)

    offset = PER_PAGE * (page - 1)
    current_query = query_name(offset=offset, limit=PER_PAGE, **query_args)
    current_query.submit_query()

    cause_404_if_no_results(current_query.parse_query_results(), page)
    return produce_response(current_query, page, offset)


def produce_response(query, page_number, offset):
    """ Get desired result output from completed query; create a response. """
    # TODO: avoid calling count more than once, expensive (though OK if cached)
    if query.output == 'json':
        return json.dumps(query.json_result)
    else:
        count = query.get_total_result_count()
        pagination = Pagination(page_number, PER_PAGE, int(count))
        result = query.parse_query_results()
        return render_template(query.jinja_template,
                               title=query.query_title,
                               pagination=pagination,
                               count=count,
                               results=result, offset=offset+1)


def cause_404_if_no_results(results, page_number):
    """ If results is an empty string or None, cause 404. """
    # TODO: Look into this; doesn't seem to apply for the SPARQL responses.
    if not results and page_number != 1:
        abort(404)


def parse_query_string(**kwargs):
    """ Take request.args and return a dict for passing in as **kwargs """
    return {key: json.loads(request.args.get(key)) for key in kwargs}


def url_for_other_page(page):
    args = dict(request.view_args.items() + request.args.to_dict().items())
    args['page'] = page
    return url_for(request.endpoint, **args)

app.jinja_env.globals['url_for_other_page'] = url_for_other_page
