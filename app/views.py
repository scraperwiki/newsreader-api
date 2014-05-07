#!/usr/bin/env python
# encoding: utf-8
from flask import render_template, request
from app import app


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
