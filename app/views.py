#!/usr/bin/env python
# encoding: utf-8
from flask import abort, render_template, request, url_for
from app import app
from collections import namedtuple
from pagination import Pagination
import queries

PER_PAGE = 10


@app.route('/')
def index():
    """ Demo function. """
    return "Hello World!"


@app.route('/<query_to_use>', defaults={'page': 1})
@app.route('/<query_to_use>/page/<int:page>')
def show_query_results(page, query_to_use):
    # TODO: avoid calling count more than once, expensive (though OK if cached)
    query_name = getattr(queries, query_to_use)
    query = query_name()
    count = query.get_total_result_count()
    offset = PER_PAGE * (page - 1)
    results = get_results_for_page(query_name, PER_PAGE, offset)

    if not results and page != 1:
        abort(404)

    pagination = Pagination(page, PER_PAGE, int(count))
    # TODO: May need to handle template differently for different queries.
    return render_template('paginate.html', title='Query 3 results',
                           pagination=pagination, count=count,
                           results=results, offset=offset+1)


def get_results_for_page(query_name, results_per_page, offset):
    # TODO: Need to handle other arguments.
    query = query_name(offset=offset, limit=results_per_page)
    query.submit_query()
    # TODO: This result is hardcoded; need to move into class.
    return parse_query3_results(query.json_result)


def url_for_other_page(page):
    args = dict(request.view_args.items() + request.args.to_dict().items())
    args['page'] = page
    return url_for(request.endpoint, **args)

app.jinja_env.globals['url_for_other_page'] = url_for_other_page


def parse_query3_results(json_query_results):
    Query3Result = namedtuple('Query3Result', 'entity_type count')
    results = []
    for result in json_query_results['results']['bindings']:
        entity_type = result['type']['value']
        count = result['n']['value']
        results.append(Query3Result(entity_type, count))
    return results
