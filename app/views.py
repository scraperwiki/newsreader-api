#!/usr/bin/env python
# encoding: utf-8
from flask import abort, render_template, request, url_for
from app import app
from collections import namedtuple
from pagination import Pagination
import query3

PER_PAGE = 10


@app.route('/')
def index():
    """ Demo function. """
    return "Hello World!"


@app.route('/testpaging', defaults={'page': 1})
@app.route('/testpaging/page/<int:page>')
def show_query3_results(page):
    # TODO: avoid calling count more than once, expensive (though OK if cached)
    count = get_query_3_result_count()
    offset = PER_PAGE * (page - 1)
    results = get_results_for_page(page, PER_PAGE, offset)

    if not results and page != 1:
        abort(404)

    pagination = Pagination(page, PER_PAGE, int(count))
    return render_template('paginate.html', title='Query 3 results',
                           pagination=pagination, count=count,
                           results=results, offset=offset+1)


def get_results_for_page(page, results_per_page, offset):
    # TODO: use limit of 100 by default for now; consider allowing variation
    query = query3.create_sparql_query(query3.sparql_template_array, 1,
                                       offset, limit=results_per_page)
    json_query_results = query3.perform_sparql_query(query)
    return parse_query3_results(json_query_results)


def url_for_other_page(page):
    args = dict(request.view_args.items() + request.args.to_dict().items())
    args['page'] = page
    return url_for(request.endpoint, **args)

app.jinja_env.globals['url_for_other_page'] = url_for_other_page


def get_query_3_result_count():
    json_count_result = \
        query3.perform_sparql_query(query3.create_count_query())
    return json_count_result['results']['bindings'][0]['n']['value']


def parse_query3_results(json_query_results):
    Query3Result = namedtuple('Query3Result', 'entity_type count')
    results = []
    for result in json_query_results['results']['bindings']:
        entity_type = result['type']['value']
        count = result['n']['value']
        results.append(Query3Result(entity_type, count))
    return results
