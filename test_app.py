#!/usr/bin/env python
# encoding: utf-8
from flask import Flask, request

app = Flask(__name__)


@app.route('/')
def index():
    """ Demo function. """
    return "Hello World!"


@app.route('/simple/query1')
def handle_offset_and_limit():
    """ Simple query string function. """
    offset = request.args.get('offset')
    limit = request.args.get('limit')
    return "offset {0}, limit {1}".format(offset, limit)


def main():
    """ Start Flask. """
    app.run(debug=True)


if __name__ == '__main__':
    main()
