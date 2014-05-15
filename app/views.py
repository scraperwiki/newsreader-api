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


@app.route('/testpaging', defaults={'page': 1})
@app.route('/testpaging/page/<int:page>')
def show_query3_results(page):
    # TODO: avoid calling count more than once, expensive (though OK if cached)
    query_3 = queries.EntitiesThatAreActorsQuery()
    count = query_3.get_total_result_count()
    offset = PER_PAGE * (page - 1)
    results = get_results_for_page(PER_PAGE, offset)

    if not results and page != 1:
        abort(404)

    pagination = Pagination(page, PER_PAGE, int(count))
    return render_template('paginate.html', title='Query 3 results',
                           pagination=pagination, count=count,
                           results=results, offset=offset+1)


def get_results_for_page(results_per_page, offset):
    query_3 = queries.EntitiesThatAreActorsQuery(offset=offset,
                                                 limit=results_per_page)
    query_3.submit_query()
    return parse_query3_results(query_3.json_result)


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
