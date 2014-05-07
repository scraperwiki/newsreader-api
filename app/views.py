#!/usr/bin/env python
# encoding: utf-8
from flask import render_template, request
from app import app
import query3


@app.route('/')
def index():
    """ Demo function. """
    return "Hello World!"


@app.route('/simple/query3')
def handle_offset_and_limit():
    """ Simple query string function. """
    offset = request.args.get('offset')
    limit = request.args.get('limit')
    return render_template("query3.html", title='Query 3', offset=offset,
                           limit=limit)


@app.route('/test/query3')
def run_test_query():
    query = query3.create_sparql_query(query3.sparql_template_array, 1)
    return str(query3.perform_sparql_query(query))
